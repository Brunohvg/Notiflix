from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido
from libs.integracoes.api.api_whatsapp import Whatsapp
from app_mensagem.models import MensagemPadrao

WHATSAPP = Whatsapp()

@receiver(post_save, sender=Pedido)
def _enviar_msg(sender, instance, created, **kwargs):
    phone = instance.cliente.contact_phone
    nome = instance.cliente.contact_name
    status = instance.status_envio
    loja = instance.loja.nome
    user = instance.loja.usuario
    rastreio = instance.codigo_rastreio
    instance_name = instance.loja.whatsapp.instanceName 
    token = instance.loja.whatsapp.token
    
    tipo_mensagem = {
        "processando": "Pedido Pago",
        "embalado": "Pedido Embalado",
        "enviado": "Pedido Enviado",
        "devolvido": "Pedido Cancelado",
    }

    tipo_pedido = tipo_mensagem.get(status.lower())
    
    if tipo_pedido:
        try:
            # Obtém todas as mensagens padrão para o tipo de pedido e usuário específico
            msgs = MensagemPadrao.objects.filter(tipo_pedido=tipo_pedido, usuario=user)
            for msg in msgs:
                # Substitui as variáveis nas mensagens padrão
                texto_formatado = msg.mensagem_padrao.replace("[nome_cliente]", nome)
                texto_formatado = texto_formatado.replace(
                    "[numero_pedido]", str(instance.id_pedido)
                )
                texto_formatado = texto_formatado.replace("[nome_loja]", loja)
                texto_formatado = texto_formatado.replace("[link_rastreio]", rastreio)
                # Envia cada mensagem via WhatsApp
                if msg.ativado:
                    try:
                        enviado = WHATSAPP._enviar_msg(
                            instance_name=instance_name,
                            apikey=token,
                            number_phone=f"55{phone}",
                            texto=texto_formatado,
                        )
                        
                        status_code = enviado[1].get('status_code', 'No status_code found')
                        if status_code == 200:
                            return None
                    except KeyError:
                        print("Mensagem não pode ser enviada")
                else:
                    print("Mensagem não pode ser enviada")
        except MensagemPadrao.DoesNotExist:
            print(
                f"Nenhuma mensagem padrão encontrada para o tipo de pedido '{tipo_pedido}' e usuário {user}"
            )
    else:
        print(f"Status do enivo não é reconhecido: {status}")
    
