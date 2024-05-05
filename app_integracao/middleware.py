"""# middleware.py
import logging
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class IntegrationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se o usuário logado não tem uma loja associada
        if hasattr(request.user, "is_authenticated") and not hasattr(
            request.user, "loja"
        ):
            logger.debug(
                "Usuário logado, mas sem loja integrada. Redirecionando para a página de integração."
            )
            # Redirecionar para a página de integração
            return redirect(reverse("app_integracao:integracao"))

        response = self.get_response(request)
        return response"""
