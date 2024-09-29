from django.urls import path
from . import views


app_name = "app_cupom"

urlpatterns = [
    path("cupom/", views.cupom_views, name="cupom_views"),

]
