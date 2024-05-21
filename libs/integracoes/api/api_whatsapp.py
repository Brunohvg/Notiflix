import requests
import logging
from decouple import config
import secrets
import string

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Whatsapp:
    def __init__(self) -> None:
        self.APIKEY = config("APIKEY")
        if not self.APIKEY:
            raise ValueError("APIKEY não configurada")

    def _create_instancia(self, instanceName):
        url = "https://zap.lojabibelo.com.br/instance/create"
        headers = {
            "accept": "application/json",
            "apikey": self.APIKEY,
            "Content-Type": "application/json",
        }

        # Gerar um token aleatório de 8 caracteres alfanuméricos
        token = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(16)
        )

        data = {
            "instanceName": instanceName,
            "token": token,
            "qrcode": True,
            # "number": "559999999999 (Recipient number with Country Code)",
            "webhook": "https://goblin-romantic-imp.ngrok-free.app/zapi/",
            "webhook_by_events": False,
            "events": [
                "QRCODE_UPDATED",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "MESSAGES_DELETE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE",
                "CALL",
                # "MESSAGES_SET",
                # "APPLICATION_STARTUP",
                # "CONTACTS_SET",
                # "CONTACTS_UPSERT",
                # "CONTACTS_UPDATE",
                # "PRESENCE_UPDATE",
                # "CHATS_SET",
                # "CHATS_UPSERT",
                # "CHATS_UPDATE",
                # "CHATS_DELETE",
                # "GROUPS_UPSERT",
                # "GROUP_UPDATE",
                # "GROUP_PARTICIPANTS_UPDATE",
                # "NEW_JWT_TOKEN",
                # "TYPEBOT_START",
                # "TYPEBOT_CHANGE_STATUS",
            ],
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()

            qr_code_data = response_data.get("qrcode", {}).get("base64")
            if qr_code_data:
                return qr_code_data, token  # Retorna o QR Code e o token
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


"""# Exemplo de uso
if __name__ == "__main__":
    whatsapp = Whatsapp()
    instance_name = "test_instance"
    qr_code = whatsapp._create_instancia(instance_name)
    if qr_code:
        print(f"QR Code gerado com sucesso: {qr_code}")
    else:
        print("Falha ao gerar o QR Code.")"""
