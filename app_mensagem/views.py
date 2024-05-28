from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import MensagemPersonalizada
from .forms import MensagemPersonalizadaForm
from app_integracao.models import LojaIntegrada


@login_required
def lista_mensagens(request):
    loja = get_object_or_404(LojaIntegrada, usuario=request.user)
    mensagens = MensagemPersonalizada.objects.filter(loja=loja)
    return render(
        request, "app_mensagem/lista_mensagens.html", {"mensagens": mensagens}
    )


@login_required
def cria_mensagem(request):
    if request.method == "POST":
        form = MensagemPersonalizadaForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.loja = get_object_or_404(LojaIntegrada, usuario=request.user)
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
