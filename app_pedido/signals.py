from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido
from libs.integracoes.api.api_whatsapp import Whatsapp
from app_mensagem.models import MensagemPadrao

WHATSAPP = Whatsapp()

@receiver(post_save, sender=Pedido)
def _enviar_msg(sender, instance, created, **kwargs):
    phone = instance.cliente.contact_phone
    status = instance.status_pagamento 
    user = instance.loja.usuario

    if created:
        print(f"Se ha creado una nueva instancia: {phone}")
    else:
        tipos_pedidos = {
            'pago': 'Pedido Pago',
            'embalado': 'Pedido Embalado',
            'enviado': 'Pedido Enviado',
            'cancelado': 'Pedido Cancelado'
        }

        tipo_pedido = tipos_pedidos.get(status.lower())
        if tipo_pedido:
            try:
                # Obtém todas as mensagens padrão para o tipo de pedido e usuário específico
                msgs = MensagemPadrao.objects.filter(tipo_pedido=tipo_pedido, usuario=user)
                for msg in msgs:
                    # Envia cada mensagem via WhatsApp
                    WHATSAPP._enviar_msg(instance_name='319924305000', apikey='7fbhgrqj4d2x5vf0betit', number_phone=f"55{phone}", texto=msg.mensagem_padrao)
                    print(f"Mensagem enviada para {phone}: {msg.mensagem_padrao}")
            except MensagemPadrao.DoesNotExist:
                print(f"Nenhuma mensagem padrão encontrada para o tipo de pedido '{tipo_pedido}' e usuário {user}")
        else:
            print(f"Status do pagamento não é reconhecido: {status}")
        print(f"Se ha actualizado la instancia: {phone}")
