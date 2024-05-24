import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from libs.integracoes.processamento.processar_webhook import processar_eventos
from app_integracao.htmx_views import check_qrcode

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook_receiver(request, store_id):
    if request.method == "POST":
        try:
            webhook_data = json.loads(request.body)
            event_type = webhook_data.get("event")
            order_id = webhook_data.get("id")

            if not event_type or not order_id:
                logger.error("Parâmetros do webhook incompletos: %s", webhook_data)
                return JsonResponse(
                    {"error": "Parâmetros do webhook incompletos"}, status=400
                )

            if processar_eventos(store_id, event_type, order_id):
                return JsonResponse({"status": "success"}, status=200)
            else:
                logger.error("Falha ao processar o evento do webhook: %s", webhook_data)
                return JsonResponse(
                    {"error": "Falha ao processar o pedido"}, status=500
                )

        except json.JSONDecodeError:
            logger.error("Formato JSON inválido no corpo da solicitação")
            return JsonResponse(
                {"error": "Formato JSON inválido no corpo da solicitação"}, status=400
            )
    else:
        return JsonResponse(
            {"error": "Apenas solicitações POST são permitidas"}, status=405
        )


@csrf_exempt
def webhook_zap(request):
    if request.method == "POST":
        try:
            # Carregar os dados JSON do corpo da requisição
            data = json.loads(request.body)

            # Processar os dados aqui...
            event = data.get("event")

            if event == "qrcode.updated":
                base64_qrcode = data.get("data", {}).get("qrcode", {}).get("base64")

                # base64_qrcode = data["data"]["qrcode"]["code"]

                print(base64_qrcode)
            # Exemplo de processamento dos dados
            logger.info(f"Dados recebidos: {event}")

            # Retorne uma resposta de sucesso
            return JsonResponse({"message": "Success"}, status=200)
        except Exception as e:
            # Retorne uma resposta de erro em caso de exceção
            logger.error(f"Erro ao processar o webhook: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        # Retorne uma resposta de método não permitido para métodos não suportados
        return HttpResponse(status=405)
