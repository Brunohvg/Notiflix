from django.http import HttpResponse
from django.shortcuts import render


def check_qrcode(request, base64_qrcode):
    if base64_qrcode:
        context = {"base64_qrcode": base64_qrcode}
        return render(
            request, "app_integracao/page_whatsapp/blocos/qrcode_fragment.html", context
        )
    else:
        return HttpResponse("Nenhum qrcode fornecido", status=400)
