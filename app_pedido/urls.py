from django.urls import path
from . import views


app_name = "app_pedido"

urlpatterns = [
    path("pedidos/", views.pedidos, name="pedidos"),
    path("clientes/", views.clientes, name="clientes"),
    path('cliente/<int:id>/', views.detalhe_cliente, name='detalhe_cliente'),
]
