import json
import re
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

from .models import LojaIntegrada, WhatsappIntegrado
from libs.integracoes.api.api_nuvemshop import NuvemShop
from libs.integracoes.api.api_whatsapp import WhatsApp

logger = logging.getLogger(__name__)

WHATSAPP = WhatsApp()
NUVEMSHOP = NuvemShop()
PARAMETRO_CODE = "code"


def ocultar_email(email):
    """
    Oculta parte do email do usuário para privacidade.
    """
    try:
        usuario, dominio = email.split("@")
        num_ocultar = len(usuario) // 2
        usuario_oculto = "*" * num_ocultar + usuario[num_ocultar:]
        return f"{usuario_oculto}@{dominio}"
    except ValueError:
        logger.error(f"Email inválido: {email}")
        return email


def response_sem_cookie(*args, **kwargs):
    """
    Cria uma resposta HTTP sem cookies.
    """
    response = HttpResponse(*args, **kwargs)
    response.set_cookie("meu_cookie", "", max_age=0)
    return response


@login_required
def integracao(request):
    """
    Handle integration request with potential code for authorization.
    """
    code = request.GET.get(PARAMETRO_CODE, None)
    lojas = LojaIntegrada.objects.all()
    if code:
        return autorizar(request, code=code)
    return render(request, "app_integracao/base.html", {"lojas": lojas})


@login_required
def autorizar(request, code):
    """
    Authorize the store with the given code.
    """
    try:
        autorizado = NUVEMSHOP.auth_nuvem_shop(code=code)
        if not autorizado:
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
        lj_integrada = NUVEMSHOP.store_nuvem(code=access_token, store_id=user_id)
        if not lj_integrada:
            messages.error(
                request, "Erro ao obter dados da loja. Por favor, tente novamente."
            )
            return redirect("app_integracao:integracao")

        loja_id = lj_integrada.get("id")

        loja_existente = LojaIntegrada.objects.filter(id=loja_id).first()
        if loja_existente:
            if loja_existente.ativa:
                messages.error(request, "Esta loja já está integrada")
            else:
                loja_existente.ativa = True
                loja_existente.save()
                messages.success(request, "Loja reativada com sucesso")
        else:
            LojaIntegrada.objects.create(
                id=loja_id,
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
            return render(
                request, "app_integracao/base_integracao_whatsapp.html", context
            )

        messages.error(request, "Configuração não encontrada")
        return render(request, "app_integracao/base.html")

    except Exception as e:
        logger.error(f"Erro ao configurar integração: {str(e)}")
        messages.error(request, "Erro ao configurar a integração")
        return render(request, "app_integracao/base.html")


@login_required
def integra_whatsapp(request, instanceId=None):
    """
    Integrate WhatsApp with the store.
    """
    if request.method == "GET":
        return render(request, "app_integracao/base_integracao_whatsapp.html")

    if request.method == "POST":
        instanceName = request.POST.get("name")
        number = request.POST.get("id_telefone")
        # Remove o primeiro "9" após o "55" e o código de área
        new_number = re.sub(r"\D", "", "55" + number)
        new_number = re.sub(r"(?<=^55\d{2})9", "", new_number)
        loja = request.user.loja

        try:
            # Check if the number is already integrated
            if WhatsappIntegrado.objects.filter(instanceName=instanceName).exists():
                messages.error(
                    request,
                    f"Esse número: {instanceName}, já está integrado ao sistema e pertence a outra loja.",
                )
                return redirect("app_integracao:integra_whatsapp")

            # Check if the store already has a WhatsApp account
            if hasattr(loja, "whatsapp"):
                messages.error(
                    request, "Esta loja já tem uma conta de WhatsApp em uso."
                )
                return redirect("app_integracao:integracao")

            # Create new WhatsApp instance
            qr_code_base64, token, instanceId, status = WHATSAPP.create_instance(
                instanceName,
                instanceId,
                #new_number,
            )
            if not qr_code_base64:
                messages.error(request, "Falha ao gerar o QR Code.")
                return redirect("app_integracao:integracao")

            # Save the instance to the database
            try:
                WhatsappIntegrado.objects.create(
                    instanceId=instanceId,
                    instanceName=instanceName,
                    loja=loja,
                    qr_code_image=qr_code_base64,
                    token=token,
                    status=status,
                    numero=new_number,
                )
                messages.success(request, "WhatsApp integrado com sucesso.")
            except IntegrityError:
                messages.error(request, "Erro ao salvar a integração do WhatsApp.")
                return redirect("app_integracao:integracao")

            return redirect(
                reverse("app_integracao:config_integracao", args=[instanceId])
            )

        except Exception as e:
            logger.error(f"Erro durante a integração do WhatsApp: {str(e)}")
            messages.error(
                request, f"Ocorreu um erro durante a criação do WhatsApp: {str(e)}"
            )

    return render(request, "app_integracao/base_integracao_whatsapp.html")
