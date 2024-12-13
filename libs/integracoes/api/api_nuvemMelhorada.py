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
            logger.critical("CLIENT_ID ou CLIENT_SECRET não configurados")
            raise ValueError("CLIENT_ID ou CLIENT_SECRET não configurados")
        logger.info("NuvemShop inicializado com sucesso.")

    def auth_nuvem_shop(self, code):
        """
        Autentica a aplicação na Nuvem Shop usando o código de autorização.
        """
        logger.info("Iniciando autenticação com o código: %s", code)
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
            logger.info("Autenticação bem-sucedida.")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error("Erro na autenticação: %s", e)
            return None

    def store_nuvem(self, code, store_id):
        """
        Obtém informações da loja da Nuvem Shop.
        """
        logger.info("Obtendo informações da loja com ID: %s", store_id)
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/store"
        headers = {
            "Authentication": f"bearer {code}",
            "User-Agent": "CloudStore (cloudstore@email.com)",
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info("Informações da loja obtidas com sucesso.")
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
            logger.error("Erro ao obter informações da loja: %s", http_err)
        except requests.exceptions.RequestException as req_err:
            logger.error("Erro na solicitação HTTP: %s", req_err)
        except Exception as e:
            logger.error("Erro inesperado: %s", e)
        return None

    def _make_api_request(self, url, code, store_id, method="GET", payload=None):
        """
        Faz uma requisição à API da Nuvem Shop.
        """
        logger.info("Fazendo requisição %s para a URL: %s", method, url)
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
            logger.info("Requisição %s bem-sucedida.", method)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error("Erro HTTP: %s", http_err)
        except requests.exceptions.RequestException as req_err:
            logger.error("Erro na solicitação HTTP: %s", req_err)
        except Exception as e:
            logger.error("Erro inesperado: %s", e)
        return None

    def _post_create_webhook(self, code, store_id, url_webhook, event):
        """
        Cria um webhook na Nuvem Shop.
        """
        logger.info("Criando webhook para o evento: %s", event)
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks"
        payload = {"url": url_webhook, "event": event}
        return self._make_api_request(url, code, store_id, method="POST", payload=payload)

    def _post_create_webhooks_batch(self, code, store_id, url_webhook, events):
        """
        Cria múltiplos webhooks na Nuvem Shop.
        """
        logger.info("Criando múltiplos webhooks para os eventos: %s", events)
        results = []
        for event in events:
            result = self._post_create_webhook(code, store_id, url_webhook, event)
            results.append(result)
        return results

    def _post_modificar_webhook(self, code, store_id):
        """
        Modifica um webhook existente na Nuvem Shop.
        """
        logger.info("Modificando webhook na loja ID: %s", store_id)
        payload = {
            "id": "16955277",
            "url": "https://goblin-romantic-imp.ngrok-free.app/webhook/",
            "event": "order/paid",
        }
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/"
        return self._make_api_request(url, code, store_id, method="PUT", payload=payload)

    def _get_webhook(self, code, store_id):
        """
        Obtém webhooks configurados na Nuvem Shop.
        """
        logger.info("Obtendo webhooks configurados para a loja ID: %s", store_id)
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/"
        return self._make_api_request(url, code, store_id, method="GET")

    def _deletar_webhook(self, code, store_id, id_webhook):
        """
        Deleta um webhook na Nuvem Shop.
        """
        logger.info("Deletando webhook ID: %s da loja ID: %s", id_webhook, store_id)
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/{id_webhook}"
        return self._make_api_request(url, code, store_id, method="DELETE")

    def _get_pedidos(self, code, store_id, id_pedido):
        """
        Obtém detalhes de um pedido específico na Nuvem Shop.
        """
        logger.info("Obtendo detalhes do pedido ID: %s", id_pedido)
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/orders/{id_pedido}"
        return self._make_api_request(url, code, store_id, method="GET")

    def _get_pedido(self, code, store_id):
        """
        Obtém uma lista de pedidos na Nuvem Shop.
        """
        logger.info("Obtendo lista de pedidos para a loja ID: %s", store_id)
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/orders/"
        return self._make_api_request(url, code, store_id, method="GET")

    def _get_checkout(self, code, store_id):
        """
        Obtém uma lista de checkouts na Nuvem Shop.
        """
        logger.info("Obtendo lista de checkouts para a loja ID: %s", store_id)
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/checkouts/"
        return self._make_api_request(url, code, store_id, method="GET")

# Exemplo de uso
"""if __name__ == "__main__":
    nuvem_shop = NuvemShop()
    store_id = "2686287"
    results = nuvem_shop._get_checkout(
        code="dc8e4d40cf2cfa8512d8784d53ecc4b394f168ec",
        store_id=store_id,
    )
    print(results)"""