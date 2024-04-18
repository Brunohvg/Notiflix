from django.urls import path
from . import views


app_name = "app_profile"

urlpatterns = [
    path("login", views.authenticacao, name="authenticacao"),
    path("deslogar", views.deslogar, name="deslogar"),
    path("registre-se", views.cadastrar_usuario, name="registrar"),
    path("profile", views.perfil, name="profile"),
]
