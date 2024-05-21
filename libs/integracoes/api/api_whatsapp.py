import requests
import logging
from decouple import config

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Whatsapp:
    def __init__(self) -> None:
        self.APIKEY = config("APIKEY")
        if not self.APIKEY:
            raise ValueError("APIKEY não configurada")

    def _create_instancia(self, instanceName, token=None):
        url = "https://zap.lojabibelo.com.br/instance/create"
        headers = {
            "accept": "application/json",
            "apikey": self.APIKEY,
            "Content-Type": "application/json",
        }
        data = {
            "instanceName": instanceName,
            "token": "token",
            "qrcode": True,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()

            qr_code_data = response_data.get("qrcode", {}).get("base64")
            if qr_code_data:
                return qr_code_data
            else:
                logger.warning("Código QR não encontrado na resposta da API.")
                return None
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Erro na solicitação HTTP: {e.response.status_code} - {e.response.text}"
            )
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na solicitação: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None


# Exemplo de uso
if __name__ == "__main__":
    whatsapp = Whatsapp()
    instance_name = "test_instance"
    # token = "your_token_here"
    qr_code = whatsapp._create_instancia(instance_name)
    if qr_code:
        print(f"QR Code gerado com sucesso: {qr_code}")
    else:
        print("Falha ao gerar o QR Code.")

"""# Instância da classe Whatsapp
whatsapp_instance = Whatsapp()
qr_code_bytes = whatsapp_instance._create_instancia(
    instanceName="lojabibelo1", token="12451"
)
print(whatsapp_instance)"""
