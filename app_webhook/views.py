import json
import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from libs.integracoes.processamento.processar_webhook import processar_eventos
from app_integracao.models import WhatsappIntegrado  # Importar o modelo
from libs.integracoes.api.api_whatsapp import WhatsApp


logger = logging.getLogger(__name__)
WHATSAPP = WhatsApp()

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
    if request.method != "POST":
        return error_response("Apenas solicitações POST são permitidas", 405)

    try:
        data = json.loads(request.body)
        logger.info(f"Dados recebidos: {data}")
        return process_webhook(data, id)
    except json.JSONDecodeError:
        return error_response("Formato JSON inválido no corpo da solicitação", 400)
    except Exception as e:
        logger.error(f"Erro ao processar o webhook: {e}")
        return error_response("Erro interno", 500)

def process_webhook(data, id):
    event = data.get("event")
    instance_name = data.get("instance")

    whatsapp_instance = get_whatsapp_instance(instance_name)
    if not whatsapp_instance:
        return error_response("Instância não encontrada", 404)

    return handle_event(event, data, whatsapp_instance)


def error_response(message, status_code):
    logger.error(message)
    return JsonResponse({"error": message}, status=status_code)

def get_whatsapp_instance(instance_name):
    try:
        return WhatsappIntegrado.objects.get(instanceName=instance_name)
    except WhatsappIntegrado.DoesNotExist:
        logger.error(f"Instância não encontrada: {instance_name}")
        return None

def handle_event(event, data, whatsapp_instance):
    if event == "qrcode.updated":
        return handle_qrcode_update(data, whatsapp_instance)
    elif event == "connection.update":
        return handle_connection_update(data, whatsapp_instance)
    return error_response("Evento não reconhecido", 400)

def handle_qrcode_update(data, whatsapp_instance):
    base64_qrcode = data.get("data", {}).get("qrcode", {}).get("base64")
    logger.info("QRcode carregado no evento qrcode.updated")

    if base64_qrcode:
        whatsapp_instance.qr_code_image = base64_qrcode
        whatsapp_instance.save()
        logger.info(f"QRcode Atualizado na instância {whatsapp_instance.instanceName}")

        # Chama a função views_qrcode para renderizar o QR code
        return views_qrcode(None, whatsapp_instance.pk)

    return error_response("QRcode não encontrado", 400)

def handle_connection_update(data, whatsapp_instance):
    status = data.get("data", {}).get("state")
    logger.info(f"Status recebido: {status}")

    if status:
        if status == 'close':
            WHATSAPP._logout_instance(instance_name=whatsapp_instance.instanceName, token=whatsapp_instance.token)
            whatsapp_instance.status = 'close'
            whatsapp_instance.save()
            return JsonResponse({"message": "INSTANCIA FECHADAS"}, status=200)
        
        if status == 'connecting':
            whatsapp_instance.status ='connecting'
            whatsapp_instance.save()
            return JsonResponse({"message": "INSTANCIA Reconecntado"}, status=200)
        
        if status == 'open':
            whatsapp_instance.status ='open'
            whatsapp_instance.save()
            
            
            return JsonResponse({"message": "INSTANCIA CONECTADA"}, status=200)
    return error_response("Status não reconhecido", 400)

def views_qrcode(request, id):
    try:
        instancia = WhatsappIntegrado.objects.get(pk=id)
    except WhatsappIntegrado.DoesNotExist:
        return HttpResponse("QR code não encontrado na sessão", status=404)

    context = {"base64_qrcode": instancia.qr_code_image}

    return render(
        request, "app_integracao/page_whatsapp/blocos/qrcode_fragment.html", context
    )
    
