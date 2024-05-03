from django.shortcuts import render
from django.http import HttpResponse
from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from .models import Cliente, Pedido
from datetime import datetime
from django.http import JsonResponse


importar_pedidos = NuvemShop()


def pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, "app_pedido/pedido.html", {"pedidos": pedidos})


def processar_pedido(store_id, event_type, order_id):
    try:
        # Lógica para processar o pedido aqui
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        print(
            f"Este teste {loja_integrada.autorization_token}, {loja_integrada.email}, {event_type}, {order_id}"
        )
        token = loja_integrada.autorization_token

        novo_pedido = importar_pedidos._get_pedidos(
            code=token, store_id=store_id, id_pedido=order_id
        )
        print(novo_pedido)
    except LojaIntegrada.DoesNotExist:
        # Por exemplo, você pode salvar os dados do pedido no banco de dados, enviar e-mails de confirmação, etc.
        print("loja nao existe")
    # Retornar uma resposta indicando que o pedido foi processado com sucesso
    return True  # ou False dependendo do resultado do processamento
