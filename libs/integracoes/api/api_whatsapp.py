import requests
import logging
from decouple import config
import uuid

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Whatsapp:
    def __init__(self) -> None:
        self.APIKEY = config("APIKEY")
        if not self.APIKEY:
            raise ValueError("APIKEY não configurada")

    def _create_instancia(self, instanceName, instanceId):
        url = "https://zap.lojabibelo.com.br/instance/create"
        headers = {
            "accept": "application/json",
            "apikey": self.APIKEY,
            "Content-Type": "application/json",
        }

        # Gerar um token aleatório de 8 caracteres alfanuméricos
        token = str(uuid.uuid4()).upper()

        data = {
            "instanceId": instanceId,
            "instanceName": instanceName,
            "qrcode": True,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            instanceName = response_data.get("instance", {}).get("instanceName")
            instanceId = response_data.get("instance", {}).get("instanceId")
            qr_code_data = response_data.get("qrcode", {}).get("base64")
            status = response_data.get("instance", {}).get("status")

            if instanceId and instanceName:
                webhook_url = (
                    f"https://zap.lojabibelo.com.br/webhook/set/{instanceName}"
                )
                webhook_data = {
                    "url": f"https://goblin-romantic-imp.ngrok-free.app/zapi/{instanceId}/",
                    "webhook_by_events": False,
                    "webhook_base64": False,
                    "events": [
                        "QRCODE_UPDATED",
                        "CONNECTION_UPDATE",
                    ],
                }
                webhook_response = requests.post(
                    webhook_url, headers=headers, json=webhook_data
                )
                webhook_response.raise_for_status()

                if qr_code_data:
                    return (
                        qr_code_data,
                        token,
                        instanceId,
                        status,
                    )  # Retorna o QR Code e o token
            else:
                logger.warning(
                    "instanceId ou instanceName não encontrado na resposta da API."
                )
                return None, None, None, None

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Erro na solicitação HTTP: {e.response.status_code} - {e.response.text}"
            )
            return None, None, None, None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na solicitação: {e}")
            return None, None, None, None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None, None, None, None


"""
# Exemplo de uso
if __name__ == "__main__":
    whatsapp = Whatsapp()
    instance_name = "test_instanceabc"
    local_instance_id = (
        "test_local_id"  # Exemplo de ID local, substitua pelo ID real em uso
    )
    qr_code, token, instanceId, status = whatsapp._create_instancia(
        instance_name, local_instance_id
    )
    if qr_code:
        print(f"QR Code gerado com sucesso: {qr_code}")
    else:
        print("Falha ao gerar o QR Code.")
"""
