# Generated by Django 5.0.4 on 2024-05-18 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_integracao', '0003_lojaintegrada_webhook_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='lojaintegrada',
            name='events',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='lojaintegrada',
            name='webhook_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
