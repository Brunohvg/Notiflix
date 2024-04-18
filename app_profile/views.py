from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Profile


def autenticar_usuario(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("nuvemshop_app:integracao")
        else:
            messages.error(request, "Usuário ou senha inválido")
    return render(request, "app_profile/login.html")


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
            novo_usuario.save()
            perfil = Profile.objects.create(
                nome=nome, whatsapp=whatsapp, user=novo_usuario
            )
            perfil.save()
            user = authenticate(request, username=email, password=senha)
            if user is not None:
                login(request, user)
                return redirect("nuvemshop_app:integracao")
            else:
                messages.error(request, "Falha ao autenticar usuário")

    return render(request, "app_profile/registrar.html")


def deslogar_usuario(request):
    logout(request)
    return redirect("autenticar_usuario")


def exibir_perfil(request):
    # Código para exibir perfil aqui
    pass


def atualizar_perfil_usuario(request):
    # Código para atualizar perfil aqui
    pass
