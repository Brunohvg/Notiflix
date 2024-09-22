from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from app_integracao.models import WhatsappIntegrado
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def check_instance(request, data, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Carrega o JSON do corpo da requisição
            instance = data.get("instancia")
            if not instance:
                return HttpResponse(
                    "Campo 'instância' ausente nos dados recebidos", status=400
                )

            # Tenta obter a instância ou criar uma nova
            whatsapp_instance, created = WhatsappIntegrado.objects.get_or_create(
                instanceName=instance
            )
            
            # Se a instância já existe e foi criada anteriormente
            if not created and whatsapp_instance.qr_code_image:
                # Chama a função check_qrcode se a instância já existe e tem QR code
                return check_qrcode(request, whatsapp_instance, data, id)

            # Se uma nova instância foi criada, você pode adicionar lógica adicional aqui

            return JsonResponse({"message": "Instância criada ou atualizada com sucesso"}, status=200)

        except json.JSONDecodeError:
            return HttpResponse("Erro ao decodificar JSON", status=400)
        except Exception as e:
            logger.error(f"Erro ao processar check_instance: {e}")
            return HttpResponse(f"Erro interno: {e}", status=500)
    else:
        return HttpResponse("Apenas solicitações POST são permitidas", status=405)


@csrf_exempt
def update_instance_status(request, data, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            instance = data.get("instancia")
            state = data.get("state")
            if not instance:
                return HttpResponse(
                    "Campo 'instância' ausente nos dados recebidos", status=400
                )

            try:
                whatsapp_instance = WhatsappIntegrado.objects.get(instanceName=instance)
                whatsapp_instance.status = state
                whatsapp_instance.save()
            except WhatsappIntegrado.DoesNotExist:
                return HttpResponse("Instância não encontrada", status=404)

            return JsonResponse(
                {"message": "Status atualizado com sucesso"}, status=200
            )
        except json.JSONDecodeError:
            return HttpResponse("Erro ao decodificar JSON", status=400)
        except Exception as e:
            logger.error(f"Erro ao atualizar o status da instância: {e}")
            return HttpResponse(f"Erro interno: {e}", status=500)
    else:
        return HttpResponse("Apenas solicitações POST são permitidas", status=405)


@csrf_exempt
def check_qrcode(request, whatsapp_instance, data, id):
    if request.method == "POST":
        try:
            qr = data.get("qrcode")
            if not qr:
                return HttpResponse(
                    "Campo 'qrcode' ausente nos dados recebidos", status=400
                )

            # Atualiza o QR code da instância
            whatsapp_instance.qr_code_image = qr
            whatsapp_instance.save()

            return views_qrcode(request, id)
        except json.JSONDecodeError:
            return HttpResponse("Erro ao decodificar JSON", status=400)
        except Exception as e:
            logger.error(f"Erro ao atualizar instância: {e}")
            return HttpResponse(f"Erro interno: {e}", status=500)
    else:
        return HttpResponse("Apenas solicitações POST são permitidas", status=405)


def views_qrcode(request, id):
    try:
        instancia = WhatsappIntegrado.objects.get(pk=id)
    except WhatsappIntegrado.DoesNotExist:
        return HttpResponse("QR code não encontrado na sessão", status=404)

    context = {"base64_qrcode": instancia.qr_code_image}

    return render(
        request, "app_integracao/page_whatsapp/blocos/qrcode_fragment.html", context
    )

"""
def teste(request):
    return render(request, "app_integracao/page_whatsapp/blocos/qrcode_fragment.html")"""