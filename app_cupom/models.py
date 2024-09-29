from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    PERCENTAGE = 'percentage'
    FIXED = 'fixed'
    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, 'Porcentagem'),
        (FIXED, 'Valor Fixo'),
    ]

    ACTIVE = 'ativo'
    EXPIRING = 'expirando'
    EXPIRED = 'expirado'
    STATUS_CHOICES = [
        (ACTIVE, 'Ativo'),
        (EXPIRING, 'Expirando'),
        (EXPIRED, 'Expirado'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Código do Cupom")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default=PERCENTAGE, verbose_name="Tipo de Desconto")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Desconto")
    expiration_date = models.DateField(verbose_name="Data de Expiração")
    uses = models.PositiveIntegerField(default=0, verbose_name="Usos Totais")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE, verbose_name="Status")

    def is_expired(self):
        return timezone.now().date() > self.expiration_date

    def save(self, *args, **kwargs):
        # Atualiza status com base na data de expiração
        if self.is_expired():
            self.status = self.EXPIRED
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome do Cliente")
    email = models.EmailField(verbose_name="E-mail")
    last_purchase_date = models.DateField(null=True, blank=True, verbose_name="Data da Última Compra")
    
    def __str__(self):
        return self.name

class CouponCriteria(models.Model):
    ALL_CUSTOMERS = 'todos'
    PURCHASED_BEFORE = 'compraram'
    NEVER_PURCHASED = 'nunca_compraram'
    PURCHASE_LAST_30_DAYS = 'compra_30_dias'
    CRITERIA_CHOICES = [
        (ALL_CUSTOMERS, 'Todos os clientes'),
        (PURCHASED_BEFORE, 'Clientes que já compraram'),
        (NEVER_PURCHASED, 'Clientes que nunca compraram'),
        (PURCHASE_LAST_30_DAYS, 'Compra nos últimos 30 dias'),
    ]
    
    criteria = models.CharField(max_length=50, choices=CRITERIA_CHOICES, verbose_name="Critério de Seleção")
    message = models.TextField(blank=True, null=True, verbose_name="Mensagem para o Cliente")

    def __str__(self):
        return self.get_criteria_display()
