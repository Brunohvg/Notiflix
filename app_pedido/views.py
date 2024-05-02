from django.shortcuts import render
from django.http import HttpResponse
from app_integracao.api.nuvemshop import NuvemShop
from .models import Cliente, Pedido
from datetime import datetime
importar_pedidos = NuvemShop()
def pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'app_pedido/pedido.html', {'pedidos': pedidos})

def sincronizar_pedidos(request):
    if request.method == 'POST':
        code = request.user.loja.autorization_token
        store_id = request.user.loja.pk
        if code and store_id:
            lista_pedidos = importar_pedidos._get_pedidos(code, store_id)
            for data in lista_pedidos:    
                nome = data['contact_name']
                email = data['contact_email']
                telefone = data['contact_phone']
                cpf = data['contact_identification']
                
                novo_cliente = Cliente.objects.create(contact_name=nome, contact_email=email, contact_phone=telefone, contact_identification=cpf)
                novo_cliente.save()  # Adicione os parênteses para chamar a função save()

                if novo_cliente:   
                    cliente = novo_cliente
                    id_venda = data['number']
                    data_pedido_str = data['created_at']
                    data_pedido = datetime.strptime(data_pedido_str, "%Y-%m-%dT%H:%M:%S+0000")
                    total = data['total']
                    status_pagamento = data['payment_status']
                    status_envio = data['shipping_status']

                    novo_pedido = Pedido.objects.create(cliente=cliente, id_venda=id_venda, data_pedido=data_pedido, total=total, status_pagamento=status_pagamento, status_envio=status_envio)
                    novo_pedido.save()

            # Após sincronizar todos os pedidos, redirecione para a página de pedidos
            return render(request, 'app_pedido/pedido.html', {'pedidos': Pedido.objects.all()})

    # Se não for uma solicitação POST, retorne a renderização da página normalmente
    return render(request, 'app_pedido/pedido.html')