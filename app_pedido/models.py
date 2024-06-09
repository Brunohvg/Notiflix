from django.db import models
from app_integracao.models import LojaIntegrada


class Cliente(models.Model):
    # Definição dos campos do cliente
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(max_length=255, verbose_name="E-mail", blank=True)
    contact_phone = models.CharField(max_length=20, verbose_name="Telefone", blank=True)
    contact_identification = models.CharField(
        max_length=100, verbose_name="CPF/CNPJ", blank=True
    )

    def __str__(self):
        return self.contact_name


class Pedido(models.Model):
    # Outros campos existentes
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    loja = models.ForeignKey(LojaIntegrada, related_name="pedidos", on_delete=models.CASCADE, null=True)
    id_venda = models.CharField(max_length=20, verbose_name="ID Venda", blank=True, null=True)
    id_pedido = models.BigIntegerField(verbose_name="Número do Pedido", blank=True)
    data_pedido = models.DateTimeField(verbose_name="Data do Pedido")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    status_pagamento = models.CharField(max_length=100, verbose_name="Status Pagamento")
    status_envio = models.CharField(max_length=100, verbose_name="Status Envio", default="Processando")
    data_pagamento = models.DateField(verbose_name="Data Pagamento", null=True, blank=True)
    data_embalado = models.DateField(verbose_name="Data Embalado", null=True, blank=True)
    data_enviado = models.DateTimeField(verbose_name="Data Enviado", null=True, blank=True)
    data_cancelado = models.DateField(verbose_name="Data Cancelado", null=True, blank=True)
    data_reembolsado = models.DateField(verbose_name="Data Reembolsado", null=True, blank=True)
    codigo_rastreio = models.CharField(max_length=100, verbose_name="Código de Rastreio", blank=True)
    ultimo_status_notificado = models.CharField(max_length=100, verbose_name="Último Status Notificado", blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id_venda} - Cliente: {self.cliente.contact_name}"

    def valor_formatado(self):
        return f"R${self.total:.2f}"
