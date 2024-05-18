from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from libs.integracoes.processamento.processar_webhook import processar_eventos

logger = logging.getLogger(__name__)


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

            # Verificar se os parâmetros essenciais estão presentes
            if not store_id or not event_type or not order_id:
                logger.error("Parâmetros do webhook incompletos: %s", webhook_data)
                return JsonResponse(
                    {"error": "Parâmetros do webhook incompletos"}, status=400
                )

            # Chamar diretamente a função ou view de tratamento de pedidos
            if processar_eventos(store_id, event_type, order_id):
                return JsonResponse({"status": "success"}, status=200)
            else:
                logger.error("Falha ao processar o evento do webhook: %s", webhook_data)
                return JsonResponse(
                    {"error": "Falha ao processar o pedido"}, status=500
                )

        except json.JSONDecodeError:
            # Se houver um erro ao analisar o JSON no corpo da solicitação
            logger.error("Invalid JSON format in request body")
            return JsonResponse(
                {"error": "Invalid JSON format in request body"}, status=400
            )
    else:
        return JsonResponse(
            {"error": "Apenas solicitações POST são permitidas"}, status=405
        )
