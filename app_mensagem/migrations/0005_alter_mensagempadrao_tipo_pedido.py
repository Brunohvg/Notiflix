# Generated by Django 5.0.4 on 2024-06-01 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_mensagem', '0004_delete_mensagempersonalizada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mensagempadrao',
            name='tipo_pedido',
            field=models.CharField(choices=[('Pedido Pago', 'Pedido Pago'), ('Pedido Embalado', 'Pedido Embalado'), ('Pedido Enviado', 'Pedido Enviado'), ('Pedido Cancelado', 'Pedido Cancelado'), ('Carrinho Abandonado', 'Carrinho Abandonado')], max_length=50),
        ),
    ]
