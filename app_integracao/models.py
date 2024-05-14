import secrets
import string
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver


class LojaIntegrada(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # ID único da Loja Integrada
    nome = models.CharField(max_length=100)
    whatsapp_phone_number = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    doc = models.CharField(max_length=14, null=True, blank=True)
    autorization_token = models.CharField(max_length=200)
    usuario = models.OneToOneField(User, related_name="loja", on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)
    url = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.nome


class WhatsappIntegrado(models.Model):
    instanceId = models.CharField(max_length=200, primary_key=True)
    instanceName = models.CharField(max_length=200)
    token = models.CharField(max_length=200)
    status = models.CharField(max_length=20, blank=True, null=True)
    loja = models.OneToOneField(
        LojaIntegrada, related_name="whatsapp", on_delete=models.CASCADE
    )  # Loja a quem essa instancia de whatsapp pertence


@receiver(pre_save, sender=WhatsappIntegrado)
def generate_token(sender, instance, **kwargs):
    if not instance.token:
        alphabet = string.ascii_letters + string.digits
        token = "".join(secrets.choice(alphabet) for _ in range(20))
        instance.token = token
