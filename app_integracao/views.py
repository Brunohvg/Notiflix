from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib import messages

from django.core.exceptions import ObjectDoesNotExist

from .models import LojaIntegrada, WhatsappIntegrado
from libs.integracoes.api.api_nuvemshop import NuvemShop

nuvemshop = NuvemShop()
PARAMETRO_CODE = "code"


def ocultar_email(email):
    usuario, dominio = email.split("@")
    num_ocultar = len(usuario) // 2
    usuario_oculto = "*" * num_ocultar + usuario[num_ocultar:]
    return usuario_oculto + "@" + dominio


def response_sem_cookie(*args, **kwargs):
    response = HttpResponse(*args, **kwargs)
    response.set_cookie(
        "meu_cookie", "", max_age=0
    )  # Configura o cookie para expirar imediatamente
    return response


# Importações omitidas por brevidade


@login_required
def integracao(request):
    code = request.GET.get(PARAMETRO_CODE, None)
    lojas = LojaIntegrada.objects.all()
    if code is not None:
        return autorizar(request, code=code)
    else:
        return render(request, "app_integracao/base.html", {"lojas": lojas})


@login_required
def autorizar(request, code):
    try:
        autorizado = nuvemshop.auth_nuvem_shop(code=code)
        access_token = autorizado.get("access_token")
        user_id = autorizado.get("user_id")

        loja_existente = LojaIntegrada.objects.filter(id=user_id).first()
        if loja_existente:
            email_oculto = ocultar_email(loja_existente.usuario.email)
            messages.error(
                request, f"Esta loja já está em uso com outro email {email_oculto}"
            )
            return redirect("app_integracao:integracao")

        if access_token and user_id:
            return loja_integrada(request, access_token, user_id)

    except Exception as e:
        messages.error(
            request, f"Ocorreu um erro durante a autorização da loja: {str(e)}"
        )

    return render(request, "app_integracao/base.html")


@login_required
def loja_integrada(request, access_token, user_id):
    try:
        usuario = request.user
        lj_integrada = nuvemshop.store_nuvem(code=access_token, store_id=user_id)
        id = lj_integrada.get("id")

        loja_existente = LojaIntegrada.objects.filter(id=id).first()
        if loja_existente:
            if loja_existente.ativa:
                messages.error(request, "Esta loja já está integrada")
            else:
                loja_existente.ativa = True
                loja_existente.save()
                messages.success(request, "Loja reativada com sucesso")
        else:
            nova_loja = LojaIntegrada.objects.create(
                id=id,
                nome=lj_integrada.get("nome"),
                whatsapp_phone_number=lj_integrada.get("whatsapp_phone_number"),
                contact_email=lj_integrada.get("contact_email"),
                email=lj_integrada.get("email"),
                doc=lj_integrada.get("doc"),
                autorization_token=access_token,
                usuario=usuario,
            )
            messages.success(request, "Loja integrada com sucesso")

    except Exception as e:
        messages.error(
            request, f"Ocorreu um erro durante a integração da loja: {str(e)}"
        )

    return redirect("app_integracao:integracao")


@login_required
def desativar_integracao(request):
    loja = get_object_or_404(LojaIntegrada, id=request.user.loja.id)

    if loja.usuario == request.user:
        cache_key = f"loja_{loja.id}_dados"
        cache.delete(cache_key)

        loja.delete()
        messages.info(request, "Sua loja foi desinstalada com sucesso")
    else:
        messages.error(request, "Você não tem permissão para desinstalar esta loja")

    return redirect("app_integracao:integracao")


@login_required
def config_integracao(request, id):
    try:
        # Verificar se o ID corresponde a uma Loja Integrada
        if LojaIntegrada.objects.filter(pk=id, usuario=request.user).exists():
            loja_integrada = LojaIntegrada.objects.get(pk=id)
            context = {"loja_integrada": loja_integrada}
            return render(request, "app_integracao/base_integracao.html", context)

        # Verificar se o ID corresponde a um Whatsapp Integrado
        elif WhatsappIntegrado.objects.filter(
            pk=id, loja__usuario=request.user
        ).exists():
            whatsapp_integrado = WhatsappIntegrado.objects.get(pk=id)
            context = {"whatsapp_integrado": whatsapp_integrado}
            return render(request, "app_integracao/base_integracao.html", context)

        # Se o ID não corresponder a nenhum dos dois, renderizar uma página de erro ou fazer o tratamento adequado
        else:
            return render(request, "app_integracao/base.html")

    except (LojaIntegrada.DoesNotExist, WhatsappIntegrado.DoesNotExist):
        # Se ocorrer uma exceção, renderizar uma página de erro ou fazer o tratamento adequado
        return render(request, "app_integracao/base.html")
