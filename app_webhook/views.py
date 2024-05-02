from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from app_integracao.api.nuvemshop import NuvemShop

get_pedidos = NuvemShop()


@csrf_exempt
def webhook_receiver(request):
    if request.method == "POST":
        try:
            # Carregar os dados JSON do corpo da solicitação
            webhook_data = json.loads(request.body)
            # Acessar os parâmetros do webhook
            store_id = webhook_data.get("store_id")
            event_type = webhook_data.get("event")
            order_id = webhook_data.get("id")

            # Fazer uma solicitação à API do serviço para obter os detalhes completos do pedido
            order_details_response = get_pedidos._get_pedidos(
                code="bc544d10a6eef47e5462ebb7b9bdc32972ff3bd3",
                store_id="2686287",
                id_pedido=order_id,
            )
            print(order_details_response)

            return JsonResponse({"status": "success"})

        except json.JSONDecodeError:
            # Se houver um erro ao analisar o JSON no corpo da solicitação
            return JsonResponse(
                {"error": "Invalid JSON format in request body"}, status=400
            )
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def webhook_receiver(request):
    if request.method == "POST":
        try:
            # Carregar os dados JSON do corpo da solicitação
            webhook_data = json.loads(request.body)
            # Processar os dados conforme necessário
            # ...

            # Retorne uma resposta com código de status 200 OK para indicar sucesso
            return JsonResponse({"status": "success"})
        except Exception as e:
            # Se ocorrer um erro durante o processamento, registre-o e retorne um código de status 500 Internal Server Error
            print(f"Error processing webhook: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)
    else:
        # Retorne um código de status 405 Method Not Allowed se a solicitação não for POST
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


"""
