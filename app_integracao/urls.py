from django.urls import path
from . import views, htmx_views


app_name = "app_integracao"

urlpatterns = [
    path("integracao/", views.integracao, name="integracao"),
    path(
        "integracao/<str:id>/", views.config_integracao, name="config_integracao"
    ),  # Corrigido aqui
    path("remover/", views.desativar_integracao, name="desativar_integracao"),
    path("integra_whatsapp/", views.integra_whatsapp, name="integra_whatsapp"),
]

htmx_urlpatterns = [
    path("check_qrcode/", htmx_views.check_qrcode, name="check_qrcode"),
]

urlpatterns += htmx_urlpatterns
