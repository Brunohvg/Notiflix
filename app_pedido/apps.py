from django.apps import AppConfig


class AppPedidoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_pedido'

    def ready(self):        
        import app_pedido.signals