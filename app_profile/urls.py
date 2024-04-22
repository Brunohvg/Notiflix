from django.urls import path
from . import views


app_name = "app_profile"

urlpatterns = [
    path("", views.autenticar_usuario, name="authenticacao"),
    path("deslogar/", views.deslogar_usuario, name="deslogar"),
    path("registre-se/", views.registrar_usuario, name="registrar"),
    path("redefinir/", views.redefinir_senha, name="redefinir"),
    path("profile/", views.exibir_perfil, name="profile"),
]
