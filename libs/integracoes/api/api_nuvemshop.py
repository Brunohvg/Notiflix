import requests
from decouple import config
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NuvemShop:
    """
    Classe para integração com a API da Nuvem Shop.
    """

    def __init__(self) -> None:
        """
        Inicializa a classe NuvemShop e configura CLIENT_ID e CLIENT_SECRET.
        """
        self.CLIENT_ID = config("CLIENT_ID")
        self.CLIENT_SECRET = config("CLIENT_SECRET")
        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            raise ValueError("CLIENT_ID ou CLIENT_SECRET não configurados")

    def auth_nuvem_shop(self, code):
        """
        Autentica a aplicação na Nuvem Shop usando o código de autorização.

        Args:
            code (str): Código de autorização.

        Returns:
            dict: Resposta da API contendo os tokens de autenticação, ou None em caso de erro.
        """
        try:
            url = "https://www.tiendanube.com/apps/authorize/token"
            data = {
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro na solicitação: {e}")
            return None

    def store_nuvem(self, code, store_id):
        """
        Obtém informações da loja da Nuvem Shop.

        Args:
            code (str): Código de autenticação.
            store_id (str): ID da loja.

        Returns:
            dict: Informações da loja, ou None em caso de erro.
        """
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/store"
        headers = {
            "Authentication": f"bearer {code}",
            "User-Agent": "CloudStore (cloudstore@email.com)",
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return {
                "nome": data["name"]["pt"],
                "doc": data["business_id"],
                "whatsapp_phone_number": data.get("whatsapp_phone_number"),
                "contact_email": data.get("contact_email"),
                "email": data.get("email"),
                "id": data["id"],
                "original_domain": data["original_domain"],
                "domains": data["domains"],
            }
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Erro HTTP: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Erro na solicitação HTTP: {req_err}")
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
        return None

    def _make_api_request(self, url, code, store_id, method="GET", payload=None):
        """
        Faz uma requisição à API da Nuvem Shop.

        Args:
            url (str): URL da API.
            code (str): Código de autenticação.
            store_id (str): ID da loja.
            method (str): Método HTTP (GET, POST, PUT, DELETE).
            payload (dict, optional): Dados para requisições POST ou PUT.

        Returns:
            dict: Resposta da API, ou None em caso de erro.
        """
        headers = {
            "Authentication": f"bearer {code}",
            "User-Agent": "CloudStore (cloudstore@email.com)",
            "Content-Type": "application/json",
        }
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=payload, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=payload, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Erro HTTP: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Erro na solicitação HTTP: {req_err}")
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
        return None

    def _post_create_webhook(self, code, store_id, url_webhook, event):
        """
        Cria um webhook na Nuvem Shop.

        Args:
            code (str): Código de autenticação.
            store_id (str): ID da loja.
            url_webhook (str): URL do webhook.
            event (str): Evento a ser monitorado pelo webhook.

        Returns:
            dict: Resposta da API, ou None em caso de erro.
        """
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks"
        payload = {"url": url_webhook, "event": event}
        return self._make_api_request(
            url, code, store_id, method="POST", payload=payload
        )

    def _post_create_webhooks_batch(self, code, store_id, url_webhook, events):
        """
        Cria múltiplos webhooks na Nuvem Shop.

        Args:
            code (str): Código de autenticação.
            store_id (str): ID da loja.
            url_webhook (str): URL do webhook.
            events (list): Lista de eventos a serem monitorados pelos webhooks.

        Returns:
            list: Lista de respostas da API para cada webhook criado.
        """
        results = []
        for event in events:
            result = self._post_create_webhook(code, store_id, url_webhook, event)
            results.append(result)
        return results

    def _post_modificar_webhook(self, code, store_id):
        """
        Modifica um webhook existente na Nuvem Shop.

        Args:
            code (str): Código de autenticação.
            store_id (str): ID da loja.

        Returns:
            dict: Resposta da API, ou None em caso de erro.
        """
        payload = {
            "id": "16955277",
            "url": "https://goblin-romantic-imp.ngrok-free.app/webhook/",
            "event": "order/paid",
        }
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/"
        return self._make_api_request(
            url, code, store_id, method="PUT", payload=payload
        )

    def _get_webhook(self, code, store_id):
        """
        Obtém webhooks configurados na Nuvem Shop.

        Args:
            code (str): Código de autenticação.
            store_id (str): ID da loja.

        Returns:
            dict: Resposta da API, ou None em caso de erro.
        """
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/"
        return self._make_api_request(url, code, store_id, method="GET")

    def _deletar_webhook(self, code, store_id, id_webhook):
        """
        Deleta um webhook na Nuvem Shop.

        Args:
            code (str): Código de autenticação.
            store_id (str): ID da loja.
            id_webhook (str): ID do webhook a ser deletado.

        Returns:
            dict: Resposta da API, ou None em caso de erro.
        """
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/{id_webhook}"
        return self._make_api_request(url, code, store_id, method="DELETE")

    def _get_pedidos(self, code, store_id, id_pedido):
        """
        Obtém detalhes de um pedido específico na Nuvem Shop.

        Args:
            code (str): Código de autenticação.
            store_id (str): ID da loja.
            id_pedido (str): ID do pedido.

        Returns:
            dict: Resposta da API, ou None em caso de erro.
        """
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/orders/{id_pedido}"
        return self._make_api_request(url, code, store_id, method="GET")

    def _get_pedido(self, code, store_id):
        """
        Obtém uma lista de pedidos na Nuvem Shop.

        Args:
            code (str): Código de autenticação.
            store_id (str): ID da loja.

        Returns:
            dict: Resposta da API, ou None em caso de erro.
        """
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/orders/"
        return self._make_api_request(url, code, store_id, method="GET")


# Exemplo de uso

nuvem_shop = NuvemShop()

store_id = "2686287"
results = nuvem_shop._get_webhook(
    code="f99079b572da305cb060f47d6cd98f5b3a6d160e",
    store_id=store_id,
)
print(results)
