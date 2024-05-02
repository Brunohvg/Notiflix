from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.webhook_receiver, name='webhook_receiver'),
]
