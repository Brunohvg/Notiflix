from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def autenticar_usuario(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("app_dashboard:dashboard")
        else:
            messages.error(request, "Usuário ou senha inválido")
    return render(request, "app_profile/login.html")


@csrf_exempt
def registrar_usuario(request):
    if request.method == "POST":
        nome = request.POST.get("nome").capitalize()
        email = request.POST.get("email")
        senha = request.POST.get("password")
        whatsapp = request.POST.get("whatsapp")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Já existe um usuário com o mesmo e-mail")
        else:
            novo_usuario = User.objects.create_user(
                username=email, email=email, password=senha
            )
            Profile.objects.create(nome=nome, whatsapp=whatsapp, user=novo_usuario)
            user = authenticate(request, username=email, password=senha)
            if user is not None:
                login(request, user)
                return redirect("app_dashboard:dashboard")
            else:
                messages.error(request, "Falha ao autenticar usuário")

    return render(request, "app_profile/registrar.html")


def redefinir_senha(request):
    if request.method == "POST":
        email = request.POST.get("emailRedefinir")
        if User.objects.filter(email=email).exists():
            # Implementar a lógica de redefinição de senha aqui
            messages.success(
                request,
                "Instruções para redefinição de senha enviadas para o e-mail fornecido.",
            )
        else:
            messages.error(request, "Não existe uma conta associada a este e-mail.")
    return render(request, "app_profile/redefinir.html")


@login_required
def deslogar_usuario(request):
    logout(request)
    return redirect("autenticar_usuario")


@login_required
def exibir_perfil(request):
    # TODO: Verificar o status de recebimento de notificações e outras lógicas necessárias
    return render(request, "app_profile/perfil.html")


@login_required
def atualizar_perfil_usuario(request):
    if request.method == "POST":
        # Implementar a lógica de atualização do perfil do usuário aqui
        messages.success(request, "Perfil atualizado com sucesso.")
    return redirect("exibir_perfil")
