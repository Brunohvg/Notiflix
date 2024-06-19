from django.shortcuts import render, redirect, HttpResponse
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
        
        # Obtenha o ID do cliente no URL da solicitação
        customer_id = request.GET.get('id')
        print(customer_id)

        # Se um ID de cliente for fornecido, filtre os clientes com base nesse ID
        if customer_id:
            cliente = Cliente.objects.get(id=customer_id)
            clientes_da_loja = [cliente]  # Lista contendo apenas o cliente específico
        else:
            # Se nenhum ID de cliente for fornecido, obtenha todos os clientes da loja
            clientes_da_loja = Cliente.objects.filter(pedido__loja=loja_do_usuario).distinct()

        return render(
            request, "app_pedido/base.html", context={"clientes": clientes_da_loja}
        )
    except ObjectDoesNotExist:
        return redirect("app_integracao:integracao")


@login_required
def detalhe_cliente(request, id):
    try:
        cliente = Cliente.objects.get(id=id)
        pedidos_do_cliente = Pedido.objects.filter(cliente=id)
        
        context = {
            'cliente': cliente,
            'pedidos': pedidos_do_cliente
        }

        return render (request, template_name='app_pedido/base_detalhe_cliente.html', context=context )
    except ObjectDoesNotExist:
        return redirect('app_integracao:integracao')


