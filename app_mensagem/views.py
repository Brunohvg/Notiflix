from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import MensagemPersonalizada, MensagemPadrao
from django.contrib.auth.models import User

@login_required
def lista_mensagens(request):
    usuario = request.user
    mensagens_personalizadas = MensagemPersonalizada.objects.filter(usuario=usuario)
    mensagens_padrao = MensagemPadrao.objects.exclude(tipo_pedido__in=[mensagem.tipo_pedido for mensagem in mensagens_personalizadas])
    mensagens = list(mensagens_personalizadas) + list(mensagens_padrao)
    return render(request, "app_mensagem/base.html", {"mensagens": mensagens})

@login_required
def edita_mensagem(request, pk):
    if request.method == "POST":
        # Obtendo o conteúdo do textarea
        text = request.POST.get("mensagem_edit")
        
        # Verificar se já existe uma mensagem personalizada com o ID pk
        mensagem_existente = MensagemPersonalizada.objects.filter(pk=pk).exists()

        if mensagem_existente:
            # Se a mensagem personalizada existir, atualize-a
            mensagem_personalizada = MensagemPersonalizada.objects.get(pk=pk)
            mensagem_personalizada.mensagem_personalizada = text
            mensagem_personalizada.save()
        else:
            # Se não existir, crie uma nova mensagem personalizada
            nova_mensagem_personalizada = MensagemPersonalizada.objects.create(
                mensagem_personalizada=text, usuario=request.user
            )
            
            # Exclua a mensagem anterior, se existir
            mensagem_anterior = MensagemPersonalizada.objects.filter(usuario=request.user).exclude(pk=nova_mensagem_personalizada.pk).first()
            if mensagem_anterior:
                mensagem_anterior.delete()

        # Obter todas as mensagens personalizadas e padrão do usuário
        usuario = request.user
        mensagens_personalizadas = MensagemPersonalizada.objects.filter(usuario=usuario)
        mensagens_padrao = MensagemPadrao.objects.exclude(tipo_pedido__in=[mensagem.tipo_pedido for mensagem in mensagens_personalizadas])
        mensagens = list(mensagens_personalizadas) + list(mensagens_padrao)
        
        # Renderizar o template com a lista de mensagens
        return render(request, "app_mensagem/base.html", {"mensagens": mensagens})



"""
@login_required
def cria_mensagem(request):
    if request.method == "POST":
        form = MensagemPersonalizadaForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.loja = get_object_or_404(User, usuario=request.user)
            mensagem.save()
            return redirect("lista_mensagens")
    else:
        form = MensagemPersonalizadaForm()
    return render(request, "app_mensagem/cria_mensagem.html", {"form": form})


@login_required
def edita_mensagem(request, pk):
    mensagem = get_object_or_404(
        MensagemPersonalizada, pk=pk, loja__usuario=request.user
    )
    if request.method == "POST":
        form = MensagemPersonalizadaForm(request.POST, instance=mensagem)
        if form.is_valid():
            form.save()
            return redirect("lista_mensagens")
    else:
        form = MensagemPersonalizadaForm(instance=mensagem)
    return render(request, "app_mensagem/edita_mensagem.html", {"form": form})
"""