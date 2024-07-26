from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido
from libs.integracoes.api.api_whatsapp import Whatsapp
from app_mensagem.models import MensagemPadrao
import logging
from celery import shared_task

logger = logging.getLogger("app_webhook")  # Nome específico para o módulo de webhook

WHATSAPP = Whatsapp()


@receiver(post_save, sender=Pedido)
def _enviar_msg(sender, instance, created, **kwargs):
    if created:
        if hasattr(instance.loja, "whatsapp") and instance.loja.whatsapp:
            if instance.loja.whatsapp.instanceName:
                enviar_msg_whatsapp.delay(instance.id)
            else:
                logger.warning(
                    "Mensagem de WhatsApp não enviada: instanceName não encontrado para o pedido %s",
                    instance.id,
                )
        else:
            logger.warning(
                "Mensagem de WhatsApp não enviada: WhatsApp não associado à loja para o pedido %s",
                instance.id,
            )


@shared_task(name="enviar_msg_whatsapp", max_retries=3, default_retry_delay=60)
def enviar_msg_whatsapp(pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        phone = pedido.cliente.contact_phone
        nome = pedido.cliente.contact_name
        status = pedido.status_envio
        loja = pedido.loja.nome
        user = pedido.loja.usuario
        rastreio = pedido.codigo_rastreio
        instance_name = pedido.loja.whatsapp.instanceName
        token = pedido.loja.whatsapp.token

        tipo_mensagem = {
            "processando": "Pedido Pago",
            "embalado": "Pedido Embalado",
            "enviado": "Pedido Enviado",
            "devolvido": "Pedido Cancelado",
        }

        tipo_pedido = tipo_mensagem.get(status.lower())

        if tipo_pedido:
            msgs = MensagemPadrao.objects.filter(tipo_pedido=tipo_pedido, usuario=user)
            for msg in msgs:
                texto_formatado = msg.mensagem_padrao.replace("[nome_cliente]", nome)
                texto_formatado = texto_formatado.replace(
                    "[numero_pedido]", str(pedido.id_pedido)
                )
                texto_formatado = texto_formatado.replace("[nome_loja]", loja)
                texto_formatado = texto_formatado.replace("[link_rastreio]", rastreio)

                if msg.ativado:
                    try:
                        enviado = WHATSAPP._enviar_msg(
                            instance_name=instance_name,
                            apikey=token,
                            number_phone=f"55{phone}",
                            texto=texto_formatado,
                        )

                        status_code = enviado[1].get(
                            "status_code", "No status_code found"
                        )
                        if status_code == 200:
                            logger.info("Mensagem enviada com sucesso para %s", phone)
                            return True
                    except KeyError:
                        logger.error("Erro ao enviar mensagem para %s", phone)
                else:
                    logger.warning("Mensagem não ativada para envio")
        else:
            logger.warning("Status do envio não reconhecido: %s", status)

    except Pedido.DoesNotExist:
        logger.error("Pedido não encontrado: %s", pedido_id)
    except Exception as e:
        logger.error("Erro ao enviar mensagem: %s", e, exc_info=True)
        return False
