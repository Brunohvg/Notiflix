import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from libs.integracoes.processamento.processar_webhook import processar_eventos
from app_integracao.htmx_views import update_instance_status, check_instance

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
        except Exception as e:
            logger.error(f"Erro ao processar o webhook: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse(
            {"error": "Apenas solicitações POST são permitidas"}, status=405
        )


@csrf_exempt
def webhook_zap(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            event = data.get("event")

            if event == "qrcode.updated":
                base64_qrcode = data.get("data", {}).get("qrcode", {}).get("base64")
                instanceId = data.get("instance")

                if base64_qrcode and instanceId:
                    data_response = {"qrcode": base64_qrcode, "instancia": instanceId}
                    return check_instance(request, data=data_response, id=id)

            logger.info(f"Dados recebidos: {event}")

            if event == "connection.update":
                status = data.get("data", {}).get("state")
                instanceId = data.get("instance")

                if status and instanceId:
                    data_response = {
                        "instancia": instanceId,
                        "state": status,
                    }
                    return update_instance_status(request, data=data_response, id=id)

            return JsonResponse({"message": "Success"}, status=200)
        except json.JSONDecodeError:
            logger.error("Formato JSON inválido no corpo da solicitação")
            return JsonResponse(
                {"error": "Formato JSON inválido no corpo da solicitação"}, status=400
            )
        except Exception as e:
            logger.error(f"Erro ao processar o webhook: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse(
            {"error": "Apenas solicitações POST são permitidas"}, status=405
        )
