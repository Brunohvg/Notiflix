from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from libs.processar_webhook import processar_eventos


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

            # Chamar diretamente a função ou view de tratamento de pedidos
            if processar_eventos(store_id, event_type, order_id):
                return JsonResponse({"status": "success"}, status=200)
            else:
                return JsonResponse(
                    {"error": "Failed to process the order"}, status=500
                )

        except json.JSONDecodeError:
            # Se houver um erro ao analisar o JSON no corpo da solicitação
            return JsonResponse(
                {"error": "Invalid JSON format in request body"}, status=400
            )
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
