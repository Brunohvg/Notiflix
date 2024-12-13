from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido
from libs.integracoes.api.api_whatsapp import WhatsApp
from app_mensagem.models import MensagemPadrao

@receiver(post_save, sender=Pedido)
def send_message(sender, instance, created, **kwargs):
    WHATSAPP = WhatsApp()  # Inicializa a API do WhatsApp

    # Obtém os dados necessários do pedido
    phone = instance.cliente.contact_phone
    nome = instance.cliente.contact_name
    status = instance.status_envio.lower()  # Converte o status para minúsculo
    loja = instance.loja.nome
    user = instance.loja.usuario
    rastreio = instance.codigo_rastreio
    instance_name = getattr(instance.loja.whatsapp, "instanceName", None)

    # Validação do nome da instância
    if not instance_name:
        print("Nome da instância do WhatsApp não encontrado.")
        return

    tipo_mensagem = {
        "processando": "Pedido Pago",
        "embalado": "Pedido Embalado",
        "enviado": "Pedido Enviado",
        "devolvido": "Pedido Cancelado",
    }

    # Verifica se o status do pedido é um dos desejados
    if status not in tipo_mensagem:
        print(f"Status do envio não reconhecido: {status}")
        return

    try:
        # Verifica se há uma instância do WhatsApp logada
        if not WHATSAPP.is_instance_logged_in(instance_name):
            print(f"Nenhuma instância do WhatsApp logada com o nome '{instance_name}'. Mensagem não enviada.")
            return

        # Obtém a mensagem padrão para o status do pedido
        tipo_pedido = tipo_mensagem[status]

        # Obtém a mensagem padrão ativada para o tipo de pedido e usuário específico
        try:
            msg = MensagemPadrao.objects.get(tipo_pedido=tipo_pedido, usuario=user, ativado=True)

            # Formata a mensagem substituindo as variáveis
            texto_formatado = msg.mensagem_padrao.replace("[nome_cliente]", nome)
            texto_formatado = texto_formatado.replace("[numero_pedido]", str(instance.id_pedido))
            texto_formatado = texto_formatado.replace("[nome_loja]", loja)
            texto_formatado = texto_formatado.replace("[link_rastreio]", rastreio)

            # Envia a mensagem via WhatsApp
            response, status = WHATSAPP.send_message(
                instance_name=instance_name,
                number_phone=f"55{phone}",
                text=texto_formatado,
            )

            # Checa o código de status da resposta
            status_code = status.get('status_code', 'No status_code found')
            if status_code == 200:
                print("Mensagem enviada com sucesso.")
            else:
                print(f"Falha ao enviar mensagem, status code: {status_code}")

        except MensagemPadrao.DoesNotExist:
            print(f"Nenhuma mensagem padrão encontrada para o tipo de pedido '{tipo_pedido}' e usuário {user}.")

    except Exception as e:
        print(f"Erro ao verificar instância do WhatsApp: {e}")
