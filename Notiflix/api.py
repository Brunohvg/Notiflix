from ninja import NinjaAPI, Router
from ninja.security import HttpBearer
from typing import Optional
from decouple import config

# Renomeando os routers importados para evitar conflito de nomes
from app_pedido.api import router as pedido_router
from app_profile.api import router as profile_router
from app_integracao.api import router as integracao_router
from app_mensagem.api import router as mensagem_router

# Classe para autenticação por token usando HttpBearer
class TokenAuth(HttpBearer):
    def authenticate(self, request, token: str) -> Optional[str]:
        # Verifique o token (aqui você pode integrar com banco de dados ou lógica customizada)
        if token == config("TOKEN_AUTH_API"):  # Substitua pela sua lógica de validação
            return token
        return None

# Instância de API com autenticação global
token_auth = TokenAuth()
api = NinjaAPI(auth=token_auth)

# Adicionando os routers com caminhos distintos
api.add_router("/pedido/", pedido_router)  # Para pedidos
api.add_router("/profile/", profile_router) # Para perfis
api.add_router("/integracao/", integracao_router)  # Para integrações
api.add_router("/mensagem/", mensagem_router)  # Para mensagens

# Certifique-se de que a aplicação está sendo executada corretamente
