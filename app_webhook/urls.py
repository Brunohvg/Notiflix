from django.urls import path
from . import views

app_name = "app_webhook"

urlpatterns = [
    path("webhook/<str:store_id>/", views.webhook_receiver, name="webhook_receiver"),
]
