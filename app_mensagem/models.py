from django.db import models
from app_integracao.models import LojaIntegrada


class MensagemPersonalizada(models.Model):
    loja = models.ForeignKey(
        LojaIntegrada, related_name="mensagens_personalizadas", on_delete=models.CASCADE
    )
    tipo_pedido = models.CharField(max_length=50)  # Ex: "confirmacao", "enviado", etc.
    ativado = models.BooleanField(default=True)
    mensagem = models.TextField()

    def __str__(self):
        return f"{self.tipo_pedido} - {self.loja.usuario.username}"
