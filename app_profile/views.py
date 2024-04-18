from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST

from django.contrib.auth.signals import user_logged_out
from django.core.cache import cache
from .models import Profile

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def authenticacao(request):
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

    else:
        return render(request, "app_profile/login.html")


@csrf_exempt
def cadastrar_usuario(request):
    if request.method == "POST":
        nome = request.POST.get("nome").capitalize()
        email = request.POST.get("email")
        senha = request.POST.get("password")
        whatsapp = request.POST.get("whatsapp")

        try:
            user = User.objects.get(email=email)
            messages.error(request, "Já existe um usuário com o mesmo e-mail")
            return render(request, "app_profile/login.html")
        except User.DoesNotExist:
            novo_usuario, criado = User.objects.get_or_create(
                username=email, email=email, defaults={"password": senha}
            )
            if criado:
                novo_usuario.set_password(senha)
                novo_usuario.save()
                # nome = nome.capitalize()
                user_perfil = Profile.objects.create(
                    nome=nome, whatsapp=whatsapp, user=novo_usuario
                )
                user_perfil.save()
                user = authenticate(request, username=email, password=senha)
                if user is not None:
                    login(request, user)
                    return redirect("nuvemshop_app:integracao")
                else:
                    messages.error(request, "Falha ao autenticar usuário")
                    return redirect("app_profile:authenticacao")
            else:
                messages.error(request, "Já existe um usuário com o mesmo e-mail")
                return render(request, "app_profile/login.html")
    else:
        return render(request, "app_profile/registrar.html")


@csrf_exempt
def deslogar(request):
    logout(request)
    return redirect("app_profile:authenticacao")


def visualizar_perfil(request):
    if request.method == "POST":
        nome = request.POST.get("inputNome")
        telefone = request.POST.get("inputTelefone")
        if nome and telefone:
            return atualizar_usuario(request, nome, telefone)

    return render(request, "app_profile/blocos/perfil.html")


def atualizar_usuario(request, nome, telefone):
    # TODO
    ...
