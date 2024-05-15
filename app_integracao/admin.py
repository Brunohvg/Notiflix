from django.contrib import admin

# Register your models here.
from .models import LojaIntegrada, WhatsappIntegrado

# Register your models here.
admin.site.register(LojaIntegrada)
admin.site.register(WhatsappIntegrado)
