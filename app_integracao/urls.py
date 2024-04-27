from django.urls import path
from . import views


app_name = "nuvemshop_app"

urlpatterns = [
    path("integracao", views.integracao, name="integracao"),
    path("remover", views.desativar_integracao, name="desativar_integracao"),]