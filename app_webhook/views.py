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
            print(f"PRINTANDO A DATA {data}")
            event = data.get("event")


            if event == "qrcode.updated":
                base64_qrcode = data.get("data", {}).get("qrcode", {}).get("base64")
                print(f"PRINTANDO A base64_qrcode {base64_qrcode}")
                instance_id = data.get("instance")
                print(f"PRINTANDO A instance_id {instance_id}")
                print(instance_id)

                if base64_qrcode and instance_id:
                    data_response = {"qrcode": base64_qrcode, "instancia": instance_id}
                    print(f"PRINTANDO A data_response {data_response}")
                    return check_instance(request, data=data_response, id=id)

            logger.info(f"Dados recebidos: {event}")

            if event == "connection.update":
                status = data.get("data", {}).get("state")
                print(f"PRINTANDO A status {status}")
                instance_id = data.get("instance")

                if status and instance_id:
                    data_response = {"instancia": instance_id, "state": status}
                    print(f"data_RESPONSE {data_response}" )
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


"""
{
  "event": "qrcode.updated",
  "instance": "BRUNO2",
  "data": {
    "qrcode": {
      "instance": "BRUNO2",
      "pairingCode": "95MNL1VK",
      "code": "2@IYfxtLFZZ9f5Y4qtJ1ja3XoZUyoehqmRxRK990cGt8FNmV+Ywg+v7w9FCSlWE2nnjBSU/BUCbfWBSNey71zw34JXxgCP+FSiPc4=,forafi6hseQxEDTU2fMO/g6oWbKrd4Ux6b7a8ZQM0FM=,6xsI9NoJeiZ9OgiUqvBn8CoPoQSUJiinSc7SL7Fiynk=,7gDdILuunkdSwOutxcpD7kXdPcDYpL5htZLJ6XXQuG4=",
      "base64": "data:image/png;base64,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"
    }
  },
  "destination": "https://webhook-test.com/9c89855f732fa68ebd872395541fd0a0",
  "date_time": "2024-09-21T01:05:12.530Z",
  "server_url": "https://api.lojabibelo.com.br",
  "apikey": "E1DC4478-0A86-4B4F-994A-54AD15CF4375"
}

"""