from django.shortcuts import render, redirect, get_object_or_404
from app_integracao.models import LojaIntegrada
from .models import Pedido, Cliente
from django.contrib.auth.decorators import login_required

def get_loja_do_usuario(user):
    """Retorna a loja associada ao usuário."""
    return user.loja

@login_required
def pedidos(request):
    loja_do_usuario = get_loja_do_usuario(request.user)
    pedidos_da_loja = Pedido.objects.filter(loja=loja_do_usuario)
    return render(request, "app_pedido/base.html", context={"pedidos": pedidos_da_loja})

@login_required
def clientes(request):
    loja_do_usuario = get_loja_do_usuario(request.user)
    customer_id = request.GET.get('id')

    if customer_id:
        cliente = get_object_or_404(Cliente, id=customer_id)
        clientes_da_loja = [cliente]  # Lista contendo apenas o cliente específico
    else:
        clientes_da_loja = Cliente.objects.filter(pedido__loja=loja_do_usuario).distinct()

    return render(request, "app_pedido/base.html", context={"clientes": clientes_da_loja})

@login_required
def detalhe_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    pedidos_do_cliente = Pedido.objects.filter(cliente=cliente)
    
    context = {
        'cliente': cliente,
        'pedidos': pedidos_do_cliente
    }

    return render(request, 'app_pedido/base_detalhe_cliente.html', context=context)