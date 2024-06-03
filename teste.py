import pika
from decouple import config
def check_rabbitmq_connection():
    # Configurações de conexão
    rabbitmq_host = 'rabbitmq.lojabibelo.com.br'  # Ou o endereço IP público do servidor
    rabbitmq_port = 5672
    rabbitmq_user = config('rabbitmq_user')
    rabbitmq_password = config('rabbitmq_password')

    # Credenciais
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)

    # Parâmetros de conexão
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        virtual_host='cloudstore',  # Certifique-se de que o vhost está correto
        credentials=credentials
    )

    try:
        # Tentando conectar ao RabbitMQ
        connection = pika.BlockingConnection(parameters)
        if connection.is_open:
            print("Conexão com RabbitMQ foi bem-sucedida!")
            connection.close()
        else:
            print("Falha na conexão com RabbitMQ.")
    except Exception as e:
        print(f"Erro ao tentar se conectar ao RabbitMQ: {e}")

if __name__ == '__main__':
    check_rabbitmq_connection()
