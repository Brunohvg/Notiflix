from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MensagemPadrao


@login_required
def lista_mensagens(request):
    usuario = request.user
    mensagens = MensagemPadrao.objects.filter(usuario=usuario)
    return render(request, "app_mensagem/base.html", {"mensagens": mensagens})


@login_required
def edita_mensagem(request, pk):
    if request.method == "POST":
        usuario = request.user
        text = request.POST.get("mensagem_edit")
        ative_id = request.POST.get("ative_id")
        # Convertendo a string 'ative_id' em um valor booleano
        ativado = bool(ative_id)
        try:
            # Tenta obter a mensagem padrão do usuário
            msg_padrao = get_object_or_404(MensagemPadrao, pk=pk, usuario=usuario)
            # Atualiza a mensagem padrão
            msg_padrao.mensagem_padrao = text
            msg_padrao.ativado = ativado
            msg_padrao.save()
            # Redireciona para a página de lista de mensagens com uma mensagem de sucesso
            # messages.success(request, "Mensagem atualizada com sucesso.")
            return redirect("app_mensagem:lista_mensagens")
        except MensagemPadrao.DoesNotExist:
            # Se a mensagem padrão não for encontrada, retorna um erro 404
            return redirect(
                "app_mensagem:lista_mensagens"
            )  # Ou renderizar uma página de erro personalizada
    else:
        # Se o método da requisição não for POST, redireciona para a página de lista de mensagens
        return redirect("app_mensagem:lista_mensagens")


@login_required
def criar_mensagem(request):
    if request.method == "POST":
        ...
    ...
