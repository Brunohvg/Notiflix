from django.db import models

class Cliente(models.Model):
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(max_length=255, verbose_name='E-mail', blank=True)
    contact_phone = models.CharField(max_length=20, verbose_name='Telefone', blank=True)
    contact_identification = models.CharField(max_length=100, verbose_name='cpf/cnpjyS', blank=True)

    def __str__(self):
        return self.contact_name

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    id_venda = models.CharField(max_length=10, verbose_name='ID Venda', blank=True)
    data_pedido = models.DateField(verbose_name='Data', blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor', blank=True)
    status_pagamento = models.CharField(max_length=100, verbose_name='Status Pagamento',blank=True)
    status_envio = models.CharField(max_length=100, verbose_name='Status Envio',blank=True)

    def __str__(self):
        return f"Pedido {self.id_venda} - Cliente: {self.cliente.contact_name}"

    def valor_formatado(self):
        return f'R${self.total:.2f}'
