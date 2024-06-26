import requests
from decouple import config
from requests.exceptions import RequestException
import logging


import requests
import json
import logging


class NuvemShop:
    def __init__(self) -> None:
        self.CLIENT_ID = config("CLIENT_ID")
        self.CLIENT_SECRET = config("CLIENT_SECRET")

    def auth_nuvem_shop(self, code):
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

            response.raise_for_status()  # Levanta HTTPError para respostas ruins

            date = response.json()
            print(date)
            return date

        except requests.exceptions.HTTPError as e:
            return f"Erro na solicitação: {e}"

    def store_nuvem(self, code, store_id):
        if code and store_id:
            url = f"https://api.nuvemshop.com.br/v1/{store_id}/store"
            headers = {
                "Authentication": f"bearer {code}",
                "User-Agent": "CloudStore (cloudstore@email.com)",
            }
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Lança uma exceção para códigos de status HTTP fora do intervalo 2xx
                data = response.json()
                store_data = {
                    "nome": data["name"]["pt"],
                    "doc": data["business_id"],
                    "whatsapp_phone_number": data["whatsapp_phone_number"],
                    "contact_email": data["contact_email"],
                    "email": data["email"],
                    "id": data["id"],
                }
                return store_data

            except requests.exceptions.HTTPError as http_err:
                logging.error(f"Erro HTTP: {http_err}")
            except requests.exceptions.RequestException as req_err:
                logging.error(f"Erro na solicitação HTTP: {req_err}")
            except Exception as e:
                logging.error(f"Erro inesperado: {e}")

        # Lidar com o erro da maneira que for apropriada para o seu aplicativo
        return None

    def _make_api_request(self, url, code, store_id, method="GET", payload=None):
        """Faz uma solicitação HTTP para a API da Nuvemshop.

        Args:
            url (str): O URL da API específico para a solicitação.
            code (str): O código de autenticação da API.
            store_id (str): O ID da loja.
            method (str): O método da solicitação HTTP (GET, POST, DELETE, etc.).
            payload (dict): Os dados a serem enviados na solicitação, se houver.

        Returns:
            dict or None: Os dados da resposta JSON da API, ou None se ocorrer um erro.
        """
        if code and store_id:
            headers = {
                "Authentication": f"bearer {code}",
                "User-Agent": "CloudStore (cloudstore@email.com)",
                "Content-Type": "application/json",  # Definindo explicitamente o tipo de conteúdo como JSON
            }
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers)
                elif method == "POST":
                    response = requests.post(url, json=payload, headers=headers)
                elif method == "PUT":
                    response = requests.post(url, json=payload, headers=headers)
                elif method == "DELETE":
                    response = requests.delete(url, headers=headers)
                else:
                    # Adicione suporte para outros métodos conforme necessário
                    pass

                response.raise_for_status()  # Lança uma exceção para códigos de status HTTP fora do intervalo 2xx
                data = response.json()

                return data

            except requests.exceptions.HTTPError as http_err:
                logging.error(f"Erro HTTP: {http_err}")
            except requests.exceptions.RequestException as req_err:
                logging.error(f"Erro na solicitação HTTP: {req_err}")
            except Exception as e:
                logging.error(f"Erro inesperado: {e}")

        # Lidar com o erro da maneira que for apropriada para o seu aplicativo
        return None

    def _post_create_webhook(self, code, store_id, url_webhook, event):
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks"
        payload = {
            "url": url_webhook,
            "event": event,
        }
        return self._make_api_request(
            url, code, store_id, method="POST", payload=payload
        )

    # WEBHOOKS
    def _post_modificar_webhook(self, code, store_id):
        payload = {
            "id": "16955277",
            "url": "https://goblin-romantic-imp.ngrok-free.app/webhook",
            "event": "order/paid",
        }
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/"
        return self._make_api_request(
            url, code, store_id, method="PUT", payload=payload
        )

    def _get_webhook(self, code, store_id):
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/"
        return self._make_api_request(url, code, store_id, method="GET")

    def _deletar_webhook(self, code, store_id, id_webhook):

        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks/{id_webhook}"
        return self._make_api_request(url, code, store_id, method="DELETE")

    def _get_pedidos(self, code, store_id, id_pedido):
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/orders/{id_pedido}"
        return self._make_api_request(url, code, store_id, method="GET")

    def _get_pedido(self, code, store_id):

        url = f"https://api.nuvemshop.com.br/v1/{store_id}/orders/"
        return self._make_api_request(url, code, store_id, method="GET")


# Exemplo de uso:
"""nuvem_shop = NuvemShop()
print(
    nuvem_shop._post_create_webhook(
        code="7b3e91b253abc1d220f1e3172cd13ed9cec4daa6",
        store_id="2685706",
        url_webhook="https://goblin-romantic-imp.ngrok-free.app/pedido_pago/",
        event="order/fulfilled",
    )
)"""

"""
nuvem_shop = NuvemShop()
print(
    nuvem_shop._get_webhook(
        code=" 126880e05c831ee784ed90ac4e0beb12674bba05",
        store_id="2685706",
    )
)"""
