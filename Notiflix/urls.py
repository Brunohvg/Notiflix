from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app_profile.urls")),
    path("", include("app_dashboard.urls")),
    path("", include("app_integracao.urls")),
    path("", include("app_pedido.urls")),
    path("", include("app_webhook.urls")),
    path("", include("app_mensagem.urls")),
]

# Add static and media URL patterns only if in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
