# ominio=ngrok http --domain=goblin-romantic-imp.ngrok-free.app 8000
"""SECRET_KEY=django-insecure-lq5q1gnzs(_b1&q&t501p5!)$+pn9!o@mkj-agiu3$65@%8vg4
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1,1b8c-2804-1b3-61c0-f1ab-d556-9931-a8a1-5a74.ngrok.io

#Dados Aplicativo Nuvemshop

CLIENT_ID=8619
CLIENT_SECRET=4263cfda2bc47a702f62d74784d7abcd97a237e1e5c3875b

ngrok http --domain=goblin-romantic-imp.ngrok-free.app 8000

dominio=ngrok http --domain=goblin-romantic-imp.ngrok-free.app 8000"""
# https://bootstrapmade.com/demo/NiceAdmin/

"""
templates/
│
├── app_dashboard/
│   ├── blocos/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── ...
│   └── ...
│
├── app_integracao/
│   ├── blocos/
│   │   ├── base.html
│   │   ├── integracao.html
│   │   └── ...
│   └── ...
│
├── app_pedido/
│   ├── blocos/
│   │   ├── base.html
│   │   ├── pedido.html
│   │   └── ...
│   └── ...
│
├── app_profile/
│   ├── blocos/
│   │   ├── base.html
│   │   ├── profile.html
│   │   └── ...
│   └── ...
│
├── app_webhook/
│   ├── blocos/
│   │   ├── base.html
│   │   ├── webhook.html
│   │   └── ...
│   └── ...
│
├── base.html  # Template base para o layout geral do site
├── home.html  # Exemplo de template específico do site
└── ...
"""


"""
templates/
│
├── pages/
│   ├── base.html
│   ├── home.html
│   └── ...
│
└── assets/
    ├── css/
    │   ├── main.css
    │   └── ...
    │
    ├── js/
    │   ├── main.js
    │   └── ...
    │
    ├── fonts/
    │   └── tabler-icons/
    │       └── ...
    │
    └── images/
        ├── backgrounds/
        ├── logos/
        ├── products/
        └── profile/


"""
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from app_integracao.models import WhatsappIntegrado
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def process_instance(request, data, id):
    """
    Processa os dados da instância, incluindo a verificação do QR Code e a atualização do status.
    """
    if request.method == "POST":
        try:
            instance = data.get("instancia")
            if not instance:
                return HttpResponse(
                    "Campo 'instância' ausente nos dados recebidos", status=400
                )

            whatsapp_instance, created = WhatsappIntegrado.objects.get_or_create(
                instanceName=instance
            )

            # Atualizar o status da instância, se aplicável
            state = data.get("state")
            if state:
                whatsapp_instance.status = state
                whatsapp_instance.save()
                return JsonResponse(
                    {"message": "Status atualizado com sucesso"}, status=200
                )

            # Atualizar o QR Code da instância
            qr = data.get("qrcode")
            if qr:
                whatsapp_instance.qr_code_image = qr
                whatsapp_instance.save()
                return views_qrcode(request, id)

            return HttpResponse("Nenhuma ação executada", status=200)

        except WhatsappIntegrado.DoesNotExist:
            return HttpResponse("Instância não encontrada", status=404)
        except Exception as e:
            logger.error(f"Erro ao processar os dados da instância: {e}")
            return HttpResponse(f"Erro interno: {e}", status=500)
    else:
        return HttpResponse("Apenas solicitações POST são permitidas", status=405)


def views_qrcode(request, id):
    """
    Exibe o QR Code da instância.
    """
    try:
        instancia = WhatsappIntegrado.objects.get(pk=id)
        context = {"base64_qrcode": instancia.qr_code_image}
        return render(
            request,
            "app_integracao/page_whatsapp/blocos/qrcode_fragment.html",
            context,
        )
    except WhatsappIntegrado.DoesNotExist:
        return HttpResponse("QR code não encontrado na sessão", status=404)


def teste(request):
    """
    Função de teste para renderizar um fragmento de QR Code.
    """
    return render(request, "app_integracao/page_whatsapp/blocos/qrcode_fragment.html")
