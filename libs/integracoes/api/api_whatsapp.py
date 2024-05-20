import requests
import qrcode
import logging
from PIL import Image
from decouple import config
from io import BytesIO


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

            qr_code_data = response_data.get("qrcode", {}).get("code")
            if qr_code_data:
                qr_code_bytes = self._generate_qr_code(qr_code_data)
                return qr_code_bytes
            else:
                logging.warning("Código QR não encontrado na resposta da API.")
                return None
        except requests.exceptions.HTTPError as e:
            logging.error(f"Erro na solicitação HTTP: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na solicitação: {e}")
            return None
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            return None

    def _generate_qr_code(self, data):
        try:
            # Criar um objeto QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Criar uma imagem PIL
            img = qr.make_image(fill_color="black", back_color="white")

            # Converter a imagem PIL para bytes
            buffered = BytesIO()

            img.save(buffered, format="PNG")
            print(img)
            return buffered.getvalue()
        except Exception as e:
            logging.error(f"Erro ao gerar QR Code: {e}")
            return None


# Instância da classe Whatsapp
whatsapp_instance = Whatsapp()
qr_code_bytes = whatsapp_instance._create_instancia(
    instanceName="lojabibelo1", token="12345678dasdas9546142w"
)


"""if qr_code_bytes:
    # Aqui você pode salvar qr_code_bytes no banco de dados
    # Exemplo de como salvar em um modelo Django
    from django.core.files.base import ContentFile
    from myapp.models import QRCodeModel  # Importe o modelo apropriado

    qr_code_instance = QRCodeModel()
    qr_code_instance.image.save("qrcode.png", ContentFile(qr_code_bytes))
    qr_code_instance.save()"""
