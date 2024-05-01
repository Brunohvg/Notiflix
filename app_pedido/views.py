from django.shortcuts import render

# Create your views here.

def pedidos(request):
    return render (request, 'app_pedido/pedido.html')