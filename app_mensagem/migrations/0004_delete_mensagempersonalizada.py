# Generated by Django 5.0.4 on 2024-06-01 02:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_mensagem', '0003_mensagempadrao_usuario_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MensagemPersonalizada',
        ),
    ]