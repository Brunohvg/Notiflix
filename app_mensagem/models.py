from django.db import models
from django.contrib.auth.models import User

tipos_pedidos = {
    'Pedido Pago': 'Pedido Pago',
    'Pedido Embalado': 'Pedido Embalado',
    'Pedido Enviado': 'Pedido Enviado',
    'Pedido Cancelado': 'Pedido Cancelado',
}


class MensagemPadrao(models.Model):
    tipo_pedido = models.CharField(max_length=50, choices=tipos_pedidos)  # Ex: "confirmacao", "enviado", etc.
    mensagem_padrao = models.TextField()
    ativado = models.BooleanField(default=True)
    editado = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.tipo_pedido} - {self.mensagem_padrao[:50]}..."

class MensagemPersonalizada(models.Model):
    usuario = models.ForeignKey(User, related_name="mensagens_personalizadas", on_delete=models.CASCADE, blank=True, null=True)
    tipo_pedido = models.CharField(max_length=50, choices=tipos_pedidos)  # Ex: "confirmacao", "enviado", etc.
    mensagem_personalizada = models.TextField()
    ativado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo_pedido}"
