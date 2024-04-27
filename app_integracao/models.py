from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self) -> str:
        return self.nome


"""class Cliente(models.Model):
    cpf_cnpj = models.CharField(max_length=14)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self) -> str:
        return self.nome


class Venda(models.Model):
    id_venda = models.CharField(max_length=20, primary_key=True)
    data = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    status_pagamento = models.CharField(max_length=50)
    status_envio = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.cliente.nome
"""
