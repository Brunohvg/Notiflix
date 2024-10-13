from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MensagemPadrao

@login_required
def lista_mensagens(request):
    """Lista as mensagens padrão do usuário."""
    usuario = request.user
    mensagens = MensagemPadrao.objects.filter(usuario=usuario)
    return render(request, "app_mensagem/base.html", {"mensagens": mensagens})



@login_required
def edita_mensagem(request):
    """Edita várias mensagens padrão do usuário de uma vez."""
    usuario = request.user
    mensagens = MensagemPadrao.objects.filter(usuario=usuario)

    if request.method == "POST":
        for idx, mensagem in enumerate(mensagens, start=1):
            text = request.POST.get(f"mensagem_edit_{idx}")
            ative_id = request.POST.get(f"ative_id_{idx}")
            ativado = bool(ative_id)

            # Verifica se o texto ou o estado de ativação foi alterado
            if mensagem.mensagem_padrao != text or mensagem.ativado != ativado:
                mensagem.mensagem_padrao = text
                mensagem.ativado = ativado
                mensagem.save()  # Salva apenas se houver alterações

                messages.success(request, "Mensagens atualizadas com sucesso.")
        
        return redirect("app_mensagem:lista_mensagens")
    
    # Se o método não for POST, renderiza a lista
    return render(request, "app_mensagem/edita_mensagem.html", {"mensagens": mensagens})


@login_required
def criar_mensagem(request):
    """Cria uma nova mensagem padrão para o usuário."""
    if request.method == "POST":
        text = request.POST.get("mensagem_nova")
        ative_id = request.POST.get("ative_id")
        ativado = bool(ative_id)

        # Cria e salva a nova mensagem padrão
        MensagemPadrao.objects.create(
            usuario=request.user,
            mensagem_padrao=text,
            ativado=ativado
        )

        messages.success(request, "Mensagem criada com sucesso.")
        return redirect("app_mensagem:lista_mensagens")
    
    return render(request, "app_mensagem/criar_mensagem.html")