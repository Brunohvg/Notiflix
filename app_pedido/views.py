from django.shortcuts import render, redirect
from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from .models import Pedido, Cliente
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# importar_pedidos = NuvemShop()


@login_required
def pedidos(request):
    try:
        loja_do_usuario = request.user.loja
        pedidos_da_loja = Pedido.objects.filter(loja=loja_do_usuario)
        return render(
            request, "app_pedido/base.html", context={"pedidos": pedidos_da_loja}
        )
    except ObjectDoesNotExist:
        return redirect("app_integracao:integracao")
    

@login_required
def clientes(request):
    try:
        loja_do_usuario = request.user.loja
        clientes_da_loja = Pedido.objects.filter(loja=loja_do_usuario)
        return render(
            request, "app_pedido/base.html", context={"clientes": clientes_da_loja}
        )
    except ObjectDoesNotExist:
        return redirect("app_integracao:integracao")
    


@login_required
def detalhes_cliente(request, cliente_id):
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        pedidos_do_cliente = cliente.pedidos.all()
        return render(request, "app_pedido/detalhes_cliente.html", context={"cliente": cliente, "pedidos": pedidos_do_cliente})
    except Cliente.DoesNotExist:
        return redirect("app_pedido:clientes")

