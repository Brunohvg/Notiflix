from django.http import HttpResponse


def check_qrcode(request):
    qrcode = request.GET.get("qrcode")
    return HttpResponse(f"qrcode:{qrcode} ")
