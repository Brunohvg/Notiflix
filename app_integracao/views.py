from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
import logging

from .models import LojaIntegrada, WhatsappIntegrado
from libs.integracoes.api.api_nuvemshop import NuvemShop
from libs.integracoes.api.api_whatsapp import Whatsapp

WHATSAPP = Whatsapp()
nuvemshop = NuvemShop()
PARAMETRO_CODE = "code"
logger = logging.getLogger(__name__)


def ocultar_email(email):
    """
    Oculta parte do email do usuário para privacidade.
    """
    try:
        usuario, dominio = email.split("@")
        num_ocultar = len(usuario) // 2
        usuario_oculto = "*" * num_ocultar + usuario[num_ocultar:]
        return usuario_oculto + "@" + dominio
    except ValueError:
        logger.error(f"Email inválido: {email}")
        return email


def response_sem_cookie(*args, **kwargs):
    """
    Cria uma resposta HTTP sem cookies.
    """
    response = HttpResponse(*args, **kwargs)
    response.set_cookie(
        "meu_cookie", "", max_age=0
    )  # Configura o cookie para expirar imediatamente
    return response


@login_required
def integracao(request):
    """
    Handle integration request with potential code for authorization.
    """
    code = request.GET.get(PARAMETRO_CODE, None)
    lojas = LojaIntegrada.objects.all()
    if code is not None:
        return autorizar(request, code=code)
    else:
        return render(request, "app_integracao/base.html", {"lojas": lojas})


@login_required
def autorizar(request, code):
    """
    Authorize the store with the given code.
    """
    try:
        autorizado = nuvemshop.auth_nuvem_shop(code=code)
        if autorizado is None:
            messages.error(request, "Erro na autorização. Por favor, tente novamente.")
            return redirect("app_integracao:integracao")

        access_token = autorizado.get("access_token")
        user_id = autorizado.get("user_id")

        if LojaIntegrada.objects.filter(id=user_id).exists():
            loja_existente = LojaIntegrada.objects.get(id=user_id)
            email_oculto = ocultar_email(loja_existente.usuario.email)
            messages.error(
                request, f"Esta loja já está em uso com outro email {email_oculto}"
            )
            return redirect("app_integracao:integracao")

        if access_token and user_id:
            return loja_integrada(request, access_token, user_id)

    except Exception as e:
        logger.error(f"Erro durante a autorização: {str(e)}")
        messages.error(
            request, f"Ocorreu um erro durante a autorização da loja: {str(e)}"
        )

    return render(request, "app_integracao/base.html")


@login_required
def loja_integrada(request, access_token, user_id):
    """
    Integrate the store with the given access token and user ID.
    """
    try:
        usuario = request.user
        lj_integrada = nuvemshop.store_nuvem(code=access_token, store_id=user_id)
        if lj_integrada is None:
            messages.error(
                request, "Erro ao obter dados da loja. Por favor, tente novamente."
            )
            return redirect("app_integracao:integracao")

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
            LojaIntegrada.objects.create(
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
        logger.error(f"Erro durante a integração da loja: {str(e)}")
        messages.error(
            request, f"Ocorreu um erro durante a integração da loja: {str(e)}"
        )

    return redirect("app_integracao:integracao")


@login_required
def desativar_integracao(request):
    """
    Deactivate the store integration.
    """
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
    """
    Configure the store or WhatsApp integration.
    """
    try:
        loja_integrada = LojaIntegrada.objects.filter(
            pk=id, usuario=request.user
        ).first()
        if loja_integrada:
            context = {"loja_integrada": loja_integrada}
            return render(request, "app_integracao/base_integracao.html", context)

        whatsapp_integrado = WhatsappIntegrado.objects.filter(
            pk=id, loja__usuario=request.user
        ).first()
        if whatsapp_integrado:
            context = {"whatsapp_integrado": whatsapp_integrado}
            return render(request, "app_integracao/base_integracao.html", context)

        messages.error(request, "Configuração não encontrada")
        return render(request, "app_integracao/base.html")

    except Exception as e:
        logger.error(f"Erro ao configurar integração: {str(e)}")
        return render(request, "app_integracao/base.html")


# Sistema de integração whatsapp


@login_required
def integra_whatsapp(request, instanceId=None):
    if request.method == "GET":
        return render(request, "app_integracao/base_integracao_whatsapp.html")

    try:
        if request.method == "POST":
            instanceName = request.POST.get("instanceName")
            loja = request.user.loja.pk

            if WhatsappIntegrado.objects.filter(instanceId=instanceId).exists():
                whatsapp_conectado = WhatsappIntegrado.objects.get(
                    instanceId=instanceId
                )
                messages.error(
                    request, f"Este número já está em uso: {whatsapp_conectado}"
                )
                return redirect("app_integracao:integracao")

            criando_instancia = WHATSAPP._create_instancia(
                instanceName=instanceName,
            )
            save_instancia = WhatsappIntegrado.objects.create(
                instanceId=instanceName,
                instanceName=instanceName,
                loja=request.user.loja,
            )
            save_instancia.save()

            return redirect("app_integracao:integracao")
    except Exception as e:
        logger.error(f"Erro durante a autorização: {str(e)}")
        messages.error(
            request, f"Ocorreu um erro durante a criação do WhatsApp: {str(e)}"
        )

    return render(request, "app_integracao/base.html")

    """
    instanceId =
    instanceName =
    status =
    loja =
    """

    ...
