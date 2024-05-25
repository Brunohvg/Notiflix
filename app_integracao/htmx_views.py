from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from app_integracao.models import WhatsappIntegrado
from django.core.exceptions import ObjectDoesNotExist


def check_instance(request, data):
    if request.method == "POST":
        try:
            instance = data["instancia"]
            whatsapp_instance, created = WhatsappIntegrado.objects.get_or_create(
                instanceName=instance
            )
            return check_qrcode(request, data, whatsapp_instance)
        except KeyError:
            return HttpResponse(
                "Campo 'instancia' ausente nos dados recebidos", status=400
            )
    else:
        return HttpResponse("Apenas solicitações POST são permitidas", status=405)


def check_qrcode(request, data, whatsapp_instance):
    if request.method == "POST":
        try:
            qr = data["qrcode"]
            whatsapp_instance.qr_code_image = qr
            whatsapp_instance.save()

            context = {"base64_qrcode": whatsapp_instance.qr_code_image}
            return views_qrcode(request, context)
        except KeyError:
            return HttpResponse(
                "Campo 'qrcode' ausente nos dados recebidos", status=400
            )
        except Exception as e:
            return HttpResponse(f"Erro ao atualizar instância: {e}", status=500)
    else:
        return HttpResponse("Apenas solicitações POST são permitidas", status=405)


def views_qrcode(request):
    # Se necessário, você pode manipular o objeto de solicitação aqui
    return render(request, "app_integracao/page_whatsapp/blocos/qrcode_fragment.html")
