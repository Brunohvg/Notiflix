from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from app_pedido.models import Cliente, Pedido
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

importar_pedidos = NuvemShop()


def processar_eventos(store_id, event_type, order_id):
    """
    Processar os eventos que estão sendo enviados pelo webhook para identificar cada processo para lidar com a situação
    """
    if event_type == "order/paid":
        return processar_pedido(store_id, event_type, order_id)
    elif event_type == "order/packed":
        return pedido_embalado(store_id, event_type, order_id)
    elif event_type == "order/fulfilled":
        return pedido_enviado(store_id, event_type, order_id)
    elif event_type == "order/cancelled":
        return pedido_cancelado(store_id, event_type, order_id)


def processar_pedido(store_id, event_type, order_id):
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        # Recuperar dados do pedido da Nuvem Shop
        try:
            novo_pedido = importar_pedidos._get_pedidos(
                code=token, store_id=store_id, id_pedido=order_id
            )
            print(novo_pedido)
        except Exception as e:
            print(f"Erro ao recuperar dados do pedido: {e}")
            return False

        # Extrair dados do cliente do pedido
        cliente_dados = {
            "contact_name": novo_pedido.get("customer", {}).get("name", ""),
            "contact_email": novo_pedido.get("customer", {}).get("email", ""),
            "contact_identification": novo_pedido.get("customer", {}).get(
                "identification", ""
            ),
            "contact_phone": novo_pedido.get("customer", {}).get("phone", ""),
            # ... (extrair outros dados do cliente se necessário)
        }

        # Tentar obter o cliente existente (opcional)
        try:
            cliente = Cliente.objects.get(contact_email=cliente_dados["contact_email"])
        except ObjectDoesNotExist:
            # Criar novo cliente se não existir
            cliente = Cliente.objects.create(**cliente_dados)

        # Converter a string de data para o formato esperado
        """        try:
            data_pedido = datetime.strptime(
                novo_pedido["created_at"], "%Y-%m-%dT%H:%M:%S%z"
            ).date()
            data_enviado = datetime.strptime(
                novo_pedido["created_at"], "%Y-%m-%dT%H:%M:%S%z"
            ).date()
        except ValueError as e:
            print(f"Erro ao converter data: {e}")
            return False"""

        # Processar o pedido utilizando o cliente recuperado ou criado
        try:
            novo_pedido_obj = Pedido.objects.create(
                cliente=cliente,
                loja=loja_integrada,
                id_pedido=novo_pedido["number"],
                id_venda=f'#{novo_pedido["id"]}',
                data_pedido=timezone.now(),
                total=novo_pedido["total"],
                status_pagamento="pago",
                # ... (outros campos do pedido)
            )
        except Exception as e:
            print(f"Erro ao criar pedido: {e}")
            return False

        # Enviar e-mail de confirmação ao cliente
        # ... (implementar lógica de envio de e-mail)

        return True

    except LojaIntegrada.DoesNotExist:
        print("Loja precisa ser integrada")
        return False


def pedido_embalado(store_id, event_type, order_id):
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        # Recuperar dados do pedido da Nuvem Shop
        try:
            novo_pedido = importar_pedidos._get_pedidos(
                code=token, store_id=store_id, id_pedido=order_id
            )
        except Exception as e:
            print(f"Erro ao recuperar dados do pedido em pedido_embalado: {e}")
            return False

        pedido = Pedido.objects.get(id_venda=novo_pedido["id"])
        pedido.data_embalado = timezone.now()
        pedido.status_envio = "Embalado"
        pedido.save()

        return True

    except (LojaIntegrada.DoesNotExist, ObjectDoesNotExist) as e:
        print("Erro ao processar pedido embalado:", e)
        return False
    except Exception as e:
        print("Erro inesperado ao processar pedido embalado:", e)
        return False


def pedido_enviado(store_id, event_type, order_id):
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        # Recuperar dados do pedido da Nuvem Shop
        try:
            novo_pedido = importar_pedidos._get_pedidos(
                code=token, store_id=store_id, id_pedido=order_id
            )
        except Exception as e:
            print(f"Erro ao recuperar dados do pedido em pedido_enviado: {e}")
            return False

        """ data_enviado = datetime.strptime(
            novo_pedido["created_at"], "%Y-%m-%dT%H:%M:%S%z"
        ).date()"""

        pedido = Pedido.objects.get(id_venda=novo_pedido["id"])
        pedido.data_enviado = timezone.now()
        pedido.status_envio = "Enviado"
        pedido.codigo_rastreio = novo_pedido["shipping_tracking_number"]
        pedido.save()

        # Enviar e-mail de notificação ao cliente
        # ... (implementar lógica de envio de e-mail)

        return True

    except (LojaIntegrada.DoesNotExist, ObjectDoesNotExist) as e:
        print("Erro ao processar pedido enviado:", e)
        return False
    except Exception as e:
        print("Erro inesperado ao processar pedido enviado:", e)
        return False


def pedido_cancelado(store_id, event_type, order_id):
    loja_integrada = LojaIntegrada.objects.get(id=store_id)
    token = loja_integrada.autorization_token
    novo_pedido = importar_pedidos._get_pedidos(
        code=token, store_id=store_id, id_pedido=order_id
    )
    print(novo_pedido)

    return True
