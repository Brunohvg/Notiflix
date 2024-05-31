from django.urls import path
from . import views

app_name = "app_mensagem"

urlpatterns = [
    path("mensagens/", views.lista_mensagens, name="lista_mensagens"),
    path("mensagens/editar/<int:pk>/", views.edita_mensagem, name="edita_mensagem"),

]

"""
    path("mensagens/nova/", views.cria_mensagem, name="cria_mensagem"),
    path("mensagens/editar/<int:pk>/", views.edita_mensagem, name="edita_mensagem"),

"""