
from decouple import config
API_URL = config(
            "API_URL", default="https://api.lojabibelo.com.br"
        )
WEBHOOK_URL = config(
            "WEBHOOK_URL", default="https://goblin-romantic-imp.ngrok-free.app"
        )

print("API_URL:", API_URL)
print("WEBHOOK_URL:", WEBHOOK_URL)