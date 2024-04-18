import requests
from decouple import config
from requests.exceptions import RequestException
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

        except RequestException as e:
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

    def _get_clientes(self, code, store_id):
        if code and store_id:
            url = f"https://api.nuvemshop.com.br/v1/{store_id}/customers?per_page=1800&q=Sem%20nome"
            headers = {
                "Authentication": f"bearer {code}",
                "User-Agent": "CloudStore (cloudstore@email.com)",
            }
            try:
                response = requests.get(url, headers=headers)
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


nuvem_shop = NuvemShop()
print(
    nuvem_shop._get_clientes(
        code=" b5d95086a6a48ff8e58e20487fdd39b044bb339b ", store_id="2685706"
    )
)
