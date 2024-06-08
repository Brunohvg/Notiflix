from django.db import models
from django.contrib.auth.models import User

tipos_pedidos = {
    "Pedido Pago": "Pedido Pago",
    "Pedido Embalado": "Pedido Embalado",
    "Pedido Enviado": "Pedido Enviado",
    "Pedido Cancelado": "Pedido Cancelado",
    "Carrinho Abandonado": "Carrinho Abandonado",
}


class MensagemPadrao(models.Model):
    usuario = models.ForeignKey(
        User,
        related_name="mensagem_padrao",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    tipo_pedido = models.CharField(
        max_length=50, choices=tipos_pedidos
    )  # Ex: "confirmacao", "enviado", etc.
    mensagem_padrao = models.TextField()
    ativado = models.BooleanField(default=True, blank=True, null=True)
    editado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tipo_pedido} - {self.mensagem_padrao[:50]}..."
