from django.contrib import admin
from .models import MensagemPersonalizada, MensagemPadrao

# Register your models here.
admin.site.register(MensagemPersonalizada)
admin.site.register(MensagemPadrao)
