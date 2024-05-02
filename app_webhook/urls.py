from django.urls import path
from . import views

app_name = "app_webhook"

urlpatterns = [
    path("pedido_pago/", views.webhook_receiver, name="webhook_receiver"),
]
