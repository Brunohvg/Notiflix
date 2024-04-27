from django.urls import path
from . import views


app_name = "app_integracao"

urlpatterns = [
    path("integracao", views.integracao, name="integracao"),
    path("remover", views.desativar_integracao, name="desativar_integracao"),]