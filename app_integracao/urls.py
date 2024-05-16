from django.urls import path
from . import views


app_name = "app_integracao"

urlpatterns = [
    path("integracao/", views.integracao, name="integracao"),
    path(
        "integracao/<str:id>/", views.config_integracao, name="config_integracao"
    ),  # Corrigido aqui
    path("remover/", views.desativar_integracao, name="desativar_integracao"),
]
