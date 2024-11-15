from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido
from libs.integracoes.api.api_whatsapp import WhatsApp
from app_mensagem.models import MensagemPadrao
import logging

logger = logging.getLogger(__name__)

if MensagemPadrao.ativado:
    @receiver(post_save, sender=Pedido)
    def send_message(sender, instance, created, **kwargs):
        WHATSAPP = WhatsApp()  # Inicializa a API do WhatsApp

        # Obtém os dados necessários do pedido
        phone = instance.cliente.contact_phone
        nome = instance.cliente.contact_name
        status = instance.status_envio.lower()
        loja = instance.loja.nome
        user = instance.loja.usuario
        rastreio = instance.codigo_rastreio
        instance_name = getattr(instance.loja.whatsapp, "instanceName", None)

        if not instance_name:
            logger.warning("Nome da instância do WhatsApp não encontrado.")
            return

        tipo_mensagem = {
            "processando": "Pedido Pago",
            "embalado": "Pedido Embalado",
            "enviado": "Pedido Enviado",
            "devolvido": "Pedido Cancelado",
        }

        if status not in tipo_mensagem:
            logger.warning(f"Status do envio não reconhecido: {status}")
            return

        try:
            if not WHATSAPP.is_instance_logged_in(instance_name):
                logger.warning(f"Nenhuma instância do WhatsApp logada com o nome '{instance_name}'. Mensagem não enviada.")
                return

            tipo_pedido = tipo_mensagem[status]

            try:
                msg = MensagemPadrao.objects.get(tipo_pedido=tipo_pedido, usuario=user, ativado=True)

                texto_formatado = msg.mensagem_padrao.replace("[nome_cliente]", nome)
                texto_formatado = texto_formatado.replace("[numero_pedido]", str(instance.id_pedido))
                texto_formatado = texto_formatado.replace("[nome_loja]", loja)
                texto_formatado = texto_formatado.replace("[link_rastreio]", rastreio)

                response, status = WHATSAPP.send_message(
                    instance_name=instance_name,
                    number_phone=f"55{phone}",
                    text=texto_formatado,
                )

                status_code = status.get('status_code', 'No status_code found')
                if status_code == 200:
                    logger.info("Mensagem enviada com sucesso.")
                else:
                    logger.error(f"Falha ao enviar mensagem, status code: {status_code}")

            except MensagemPadrao.DoesNotExist:
                logger.warning(f"Nenhuma mensagem padrão encontrada para o tipo de pedido '{tipo_pedido}' e usuário {user}.")

        except Exception as e:
            logger.error(f"Erro ao verificar instância do WhatsApp: {e}")