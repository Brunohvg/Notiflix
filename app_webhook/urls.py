from django.urls import path
from . import views

app_name = "app_webhook"

urlpatterns = [
    path("webhook/<str:store_id>/", views.webhook_receiver, name="webhook_receiver"),
    path("zapi/<str:id>/", views.webhook_zap, name="webhook_zap"),
]
