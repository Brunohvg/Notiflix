import requests
import logging
from decouple import config
import uuid

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Whatsapp:
    """
    Classe para integração com o serviço de WhatsApp.
    """
#TODO TROCAR A URL DA API POR UMA VARIAVEL 
    URL = "https://api.lojabibelo.com.br"

    def __init__(self) -> None:
        """
        Inicializa a classe Whatsapp e configura a APIKEY.
        """
        self.APIKEY = config("APIKEYS")
        if not self.APIKEY:
            raise ValueError("APIKEY não configurada")

    def _create_instancia(self, instanceName, instanceId):
        """
        Cria uma nova instância de WhatsApp e obtém o QR Code para configuração.

        Args:
            instanceName (str): Nome da instância do WhatsApp.
            instanceId (str): ID da instância do WhatsApp.

        Returns:
            tuple: Contendo QR Code em base64, token, instanceId e status.
        """
        url = f"{self.URL}/instance/create"
        headers = {
            "accept": "application/json",
            "apikey": self.APIKEY,
            "Content-Type": "application/json",
        }

        # Gerar um token aleatório de 8 caracteres alfanuméricos
        #token = str(uuid.uuid4()).upper()

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
            token = response_data.get("hash", {}).get("apikey")
            qr_code_data = response_data.get("qrcode", {}).get("base64")
            status = response_data.get("instance", {}).get("status")

            if instanceId and instanceName:
                webhook_url = f"{self.URL}/webhook/set/{instanceName}"
                webhook_data = {
                    "url": f"https://goblin-romantic-imp.ngrok-free.app/zapi/{instanceId}/",
                    "webhook_by_events": False,
                    "webhook_base64": False,
                    "events": ["QRCODE_UPDATED", "CONNECTION_UPDATE"],
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
                    )
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

    def _enviar_msg(self, instance_name, apikey, number_phone, texto):
        """
        Envia uma mensagem de texto para um número especificado usando a API de mensagens.

        Parameters:
        instance_name (str): O nome da instância da API.
        apikey (str): A chave da API para autenticação.
        number_phone (str): O número de telefone para o qual enviar a mensagem.
        texto (str): O texto da mensagem a ser enviada.

        Returns:
        dict: A resposta da API em formato JSON, se a solicitação for bem-sucedida.
        None: Se ocorrer um erro na solicitação HTTP ou se a resposta for 401 Unauthorized.
        """
        url = f"{self.URL}/message/sendText/{instance_name}"

        headers = {
            "accept": "application/json",
            "apikey": apikey,
            "Content-Type": "application/json",
        }

        data = {
            "number": number_phone,
            "options": {"delay": 1200, "presence": "composing", "linkPreview": False},
            "textMessage": {"text": texto},
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 401:
                error_response = response.json()
                logger.error(
                    f"Erro 401 Unauthorized: {error_response['response']['message']}"
                )
                return None
            response.raise_for_status()
            response_data = response.json()
            return response_data, {"status_code": 200}
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Erro na solicitação HTTP: {e.response.status_code} - {e.response.text}"
            )
            return {"status_code": 400}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na solicitação: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return {"status_code": 400}

"""# Exemplo de uso
if __name__ == "__main__":
    WHATSAPP = Whatsapp()
    result = WHATSAPP._enviar_msg('31973121650', '5721C91E-D2DC-4563-B8D7-3E64CBEF33CE', '5531973121650', 'esse é um teste')
    if result is None:
        print("Falha ao enviar a mensagem")
    else:
        print(result)
"""