from django.urls import path
from . import views


app_name = "app_pedido"

urlpatterns = [
    path("pedidos/", views.pedidos, name="pedidos"),

]
