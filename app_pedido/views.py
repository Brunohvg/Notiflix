from django.shortcuts import render
from django.http import HttpResponse
from app_integracao.api.nuvemshop import NuvemShop
from .models import Cliente, Pedido
from datetime import datetime
from django.http import JsonResponse

importar_pedidos = NuvemShop()


def pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, "app_pedido/pedido.html", {"pedidos": pedidos})


def processar_pedido(store_id, event_type, order_id):
    # Lógica para processar o pedido aqui
    # Por exemplo, você pode salvar os dados do pedido no banco de dados, enviar e-mails de confirmação, etc.
    print(
        f"store_id: nova viwes {store_id}, event_type: {event_type}, order_id: {order_id}"
    )
    # Retornar uma resposta indicando que o pedido foi processado com sucesso
    return True  # ou False dependendo do resultado do processamento
