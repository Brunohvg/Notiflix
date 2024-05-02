from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app_profile.urls")),
    path("", include("app_dashboard.urls")),
    path("",include("app_integracao.urls")),
    path("", include('app_pedido.urls')),
    path("", include('app_webhook.urls')),
]
