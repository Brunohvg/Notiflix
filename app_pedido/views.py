from django.shortcuts import render
from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada


importar_pedidos = NuvemShop()


def pedidos(request):

    return render(request, "app_pedido/pedido.html")
