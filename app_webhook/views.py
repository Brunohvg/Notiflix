from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def webhook_receiver(request):
    if request.method == 'POST':
        # Processar os dados recebidos do webhook
        # Aqui você pode acessar os dados do pedido e fazer o que for necessário
        # por exemplo, atualizar o status do pedido, registrar o evento, etc.
        webhook_data = request.POST  
        print(webhook_data)
        # Depois de processar os dados, retorne uma resposta adequada ao serviço que enviou o webhook
        return JsonResponse({'status': 'success'})
    else:
        # Se a solicitação não for POST, retorne um erro ou uma resposta adequada
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
