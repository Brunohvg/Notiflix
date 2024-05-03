from django.db import models
from app_integracao.models import LojaIntegrada


class Cliente(models.Model):
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(max_length=255, verbose_name="E-mail", blank=True)
    contact_phone = models.CharField(max_length=20, verbose_name="Telefone", blank=True)
    contact_identification = models.CharField(
        max_length=100, verbose_name="cpf/cnpj", blank=True
    )

    def __str__(self):
        return self.contact_name


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    loja = models.ForeignKey(LojaIntegrada, on_delete=models.CASCADE, null=True)
    id_venda = models.CharField(max_length=10, verbose_name="ID Venda", blank=True)
    data_pedido = models.DateField(verbose_name="Data", blank=True)
    total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Valor", blank=True
    )
    status_pagamento = models.CharField(
        max_length=100, verbose_name="Status Pagamento", blank=True
    )
    status_envio = models.CharField(
        max_length=100, verbose_name="Status Envio", blank=True
    )

    def __str__(self):
        return f"Pedido {self.id_venda} - Cliente: {self.cliente.contact_name}"

    def valor_formatado(self):
        return f"R${self.total:.2f}"


"""
from django.db import models

class Order(models.Model):
    id = models.AutoField(primary_key=True)

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    next_action = models.CharField(max_length=50)

    shipping = models.ForeignKey('Shipping', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20)

    # Opcional:
    products = models.ManyToManyField('Product', through='OrderProduct')

class Customer(models.Model):
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)

class Shipping(models.Model):
    shipping_option = models.CharField(max_length=50)
    shipping_tracking_number = models.CharField(max_length=100, null=True, blank=True)

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class Product(models.Model):
    name = models.CharField(max_length=255)

"""
