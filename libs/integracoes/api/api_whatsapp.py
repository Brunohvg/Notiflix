import requests
import logging
from decouple import config
from django.http import JsonResponse, HttpResponse

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsApp:
    """
    Classe para integração com o serviço de WhatsApp.
    """

    def __init__(self):
        """
        Inicializa a classe WhatsApp e configura a API_KEY e API_URL.
        """
        self.API_KEY = config("API_KEY")  # Renomeado para API_KEY
        self.API_URL = config(
            "API_URL", default="https://api.lojabibelo.com.br"
        )  # Renomeado para API_URL
        self.WEBHOOK_URL = config(
            "WEBHOOK_URL", default="https://goblin-romantic-imp.ngrok-free.app"
        )

        if not self.API_KEY:
            raise ValueError("API_KEY não configurada")
        if not self.API_URL:
            raise ValueError("URL da API não configurada")
        if not self.WEBHOOK_URL:
            raise ValueError("URL de WEBHOOK Padrão não configurada")

    def is_instance_logged_in(
        self, instance_name
    ):  # Renomeado para is_instance_logged_in
        """
        Verifica se uma instância do WhatsApp está logada.

        Args:
            instance_name (str): Nome da instância do WhatsApp.

        Returns:
            bool: True se a instância estiver logada, False caso contrário.
        """
        url = f"{self.API_URL}/instance/connectionState/{instance_name}"
        headers = {
            "accept": "application/json",
            "apikey": self.API_KEY,
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            status = response_data.get("instance", {}).get("state")

            return status == "open"

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na solicitação ao verificar status da instância: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar status da instância: {e}")
            return False

    def create_instance(
        self, instance_name, instance_id, #number=''
    ):  # Renomeado para create_instance
        """
        Cria uma nova instância de WhatsApp e obtém o QR Code para configuração.

        Args:
            instance_name (str): Nome da instância do WhatsApp.
            instance_id (str): ID da instância do WhatsApp.
            number (str): Número do WhatsApp.

        Returns:
            tuple: Contendo QR Code em base64, token, instance_id e status.
        """
        url = f"{self.API_URL}/instance/create"
        headers = {
            "accept": "application/json",
            "apikey": self.API_KEY,
            "Content-Type": "application/json",
        }

        data = {
            "instanceName": instance_name,
            "instanceId": instance_id,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True,
            #"number": number,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"Resposta da API: {response_data}")

            if isinstance(response_data, dict):
                instance = response_data.get("instance", {})
                instance_name = instance.get("instanceName")
                instance_id = instance.get("instanceId")
                token = response_data.get("hash")
                qr_code_data = response_data.get("qrcode", {}).get("base64")
                status = instance.get("status")

                if instance_id and instance_name:
                    self._set_webhook(instance_name, instance_id, token)
                    if qr_code_data:
                        return qr_code_data, token, instance_id, status

            logger.error("Dados inválidos na resposta da API.")
            return None, None, None, None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na solicitação: {e}")
            return None, None, None, None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None, None, None, None

    def _set_webhook(self, instance_name, instance_id, token):
        """
        Configura o webhook para a instância criada.
        """
        webhook_url = f"{self.API_URL}/webhook/set/{instance_name}"
        webhook_data = {
            "webhook": {
                "enabled": True,
                "url": f"{self.WEBHOOk_URL}/zapi/{instance_id}/",
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                "byEvents": False,
                "base64": False,
                "events": [
                    "QRCODE_UPDATED",
                    "CONNECTION_UPDATE",
                ],
            }
        }
        headers = {
            "accept": "application/json",
            "apikey": self.API_KEY,
            "Content-Type": "application/json",
        }
        try:
            webhook_response = requests.post(
                webhook_url, headers=headers, json=webhook_data
            )
            webhook_response.raise_for_status()
            logger.info(f"Webhook configurado com sucesso para {instance_name}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao configurar webhook: {e}")

    def _logout_instance(self, instance_name, token):

        logout_url = f"{self.API_URL}/instance/logout/{instance_name}"
        headers = {"apikey": token}
        try:
            logout_response = requests.post(logout_url, headers=headers)
            logout_response.raise_for_status()
            logger.info(f"logout efetuado com sucesso para {instance_name}")
            return JsonResponse({"message": "Success"}, status=200)

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na solicitação: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None

    def send_message(
        self, instance_name, number_phone, text
    ):  # Renomeado para send_message
        """
        Envia uma mensagem de texto para um número especificado usando a API de mensagens.

        Args:
            instance_name (str): O nome da instância da API.
            number_phone (str): O número de telefone para o qual enviar a mensagem.
            text (str): O texto da mensagem a ser enviada.

        Returns:
            dict: A resposta da API em formato JSON, se a solicitação for bem-sucedida.
            dict: Um dicionário contendo o status_code em caso de erro.
        """
        url = f"{self.API_URL}/message/sendText/{instance_name}"

        headers = {
            "accept": "application/json",
            "apikey": self.API_KEY,
            "Content-Type": "application/json",
        }

        data = {
            "number": number_phone,
            "options": {"delay": 1200, "presence": "composing", "linkPreview": False},
            "textMessage": {"text": text},
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json(), {"status_code": response.status_code}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na solicitação: {e}")
            return {
                "status_code": e.response.status_code if hasattr(e, "response") else 400
            }
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return {"status_code": 500}


# Exemplo de uso da classe WhatsApp
whatsapp = WhatsApp()  # Instância com nome em minúsculo
# print(whatsapp.is_instance_logged_in(instance_name='bibelo'))
# print(whatsapp.create_instance('BRUNO1', 'BRUNO1', "553192430001"))
