from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from libs.integracoes.api.api_nuvemshop import NuvemShop
import logging


URL_WEBHOOK = "cp.lojabibelo.com.br"

logger = logging.getLogger(__name__)


class LojaIntegrada(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # ID único da Loja Integrada
    nome = models.CharField(max_length=100)
    whatsapp_phone_number = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    doc = models.CharField(max_length=14, null=True, blank=True, default="")
    autorization_token = models.CharField(max_length=200)
    usuario = models.OneToOneField(User, related_name="loja", on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)
    url = models.CharField(max_length=100)
    webhook_url = models.CharField(max_length=200, blank=True, null=True)
    webhook_status = models.CharField(max_length=20, blank=True, null=True)  # Adiciona campo de status do webhook
    events = models.JSONField(default=list)  # Armazena os eventos como uma lista

    def __str__(self) -> str:
        return self.nome

    @property
    def total_pedidos(self):
        return self.pedidos.filter(status_pagamento="pago").count()

    @property
    def total_embalados(self):
        return self.pedidos.filter(status_envio="Processando").count()

    @property
    def total_enviados(self):
        return self.pedidos.filter(status_envio="Enviado").count()

    @property
    def total_cancelados(self):
        return self.pedidos.filter(status_envio="Devolvido").count()


class WhatsappIntegrado(models.Model):
    instanceId = models.CharField(max_length=200, primary_key=True)
    numero = models.CharField(max_length=200, blank=True, null=True, verbose_name="Identificação WhatsApp")
    instanceName = models.CharField(max_length=200)
    token = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    qr_code_image = models.TextField(blank=True, null=True)
    loja = models.OneToOneField(LojaIntegrada, related_name="whatsapp", on_delete=models.CASCADE)

@receiver(post_save, sender=LojaIntegrada)
def create_webhook(sender, instance, created, **kwargs):
    if created:
        try:
            nuvem_shop = NuvemShop()
            events = [
                "order/paid",
                "order/packed",
                "order/fulfilled",
                "order/cancelled",
            ]
            webhook_url = f"https://{URL_WEBHOOK}/webhook/{instance.id}/"
            logger.info(
                f"Webhook URL gerada: {webhook_url}"
            )  # Adiciona log para depuração
            results = nuvem_shop._post_create_webhooks_batch(
                code=instance.autorization_token,
                store_id=instance.id,
                url_webhook=webhook_url,
                events=events,
            )
            instance.webhook_url = webhook_url
            instance.events = events  # Armazena os eventos na loja integrada
            instance.webhook_status = "Webhook criado com sucesso !"
            instance.save()
        except Exception as e:
            instance.webhook_status = "Erro ao criar Webhook"
            instance.save()
            logger.error(f"Erro ao criar webhook para a loja {instance.id}: {e}")
