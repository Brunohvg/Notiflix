# Generated by Django 5.0.7 on 2024-10-13 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pedido', '0004_alter_pedido_id_venda'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='token_pedido',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Token Pedido'),
        ),
    ]
