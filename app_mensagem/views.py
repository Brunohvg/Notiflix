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
def edita_mensagem(request, pk):
    """Edita uma mensagem padrão do usuário."""
    usuario = request.user
    msg_padrao = get_object_or_404(MensagemPadrao, pk=pk, usuario=usuario)

    if request.method == "POST":
        text = request.POST.get("mensagem_edit")
        ative_id = request.POST.get("ative_id")
        ativado = bool(ative_id)

        # Atualiza a mensagem padrão
        msg_padrao.mensagem_padrao = text
        msg_padrao.ativado = ativado
        msg_padrao.save()

        messages.success(request, "Mensagem atualizada com sucesso.")
        return redirect("app_mensagem:lista_mensagens")
    
    # Se o método não for POST, apenas renderiza a página de edição
    return render(request, "app_mensagem/edita_mensagem.html", {"mensagem": msg_padrao})

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