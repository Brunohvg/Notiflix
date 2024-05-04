from django.shortcuts import render
from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from .models import Pedido

importar_pedidos = NuvemShop()


def pedidos(request):
    loja_do_usuario = request.user.loja
    pedidos_da_loja = Pedido.objects.filter(loja=loja_do_usuario)
    return render(
        request, "app_pedido/pedido.html", context={"pedidos": pedidos_da_loja}
    )
