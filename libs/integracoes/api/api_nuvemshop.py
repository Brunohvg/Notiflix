import requests
from decouple import config
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
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"Erro na solicitação: {e}")
            return None

    def store_nuvem(self, code, store_id):
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
            }
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"Erro HTTP: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Erro na solicitação HTTP: {req_err}")
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
        return None

    def _make_api_request(self, url, code, store_id, method="GET", payload=None):
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
            logging.error(f"Erro HTTP: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Erro na solicitação HTTP: {req_err}")
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
        return None

    def _post_create_webhook(self, code, store_id, url_webhook, event):
        url = f"https://api.nuvemshop.com.br/v1/{store_id}/webhooks"
        payload = {"url": url_webhook, "event": event}
        return self._make_api_request(
            url, code, store_id, method="POST", payload=payload
        )

    def _post_create_webhooks_batch(self, code, store_id, url_webhook, events):
        results = []
        for event in events:
            result = self._post_create_webhook(code, store_id, url_webhook, event)
            results.append(result)
        return results

    def _post_modificar_webhook(self, code, store_id):
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


"""nuvem_shop = NuvemShop()

store_id = "2685706"
results = nuvem_shop._get_webhook(
    code="5eefe8a9b5159a0cfc08c9d890aa0d93d3d905d8",
    store_id=store_id,
)
print(results)
"""