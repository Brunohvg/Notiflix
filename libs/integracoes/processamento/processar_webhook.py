from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from app_pedido.models import Cliente, Pedido
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import logging

# TODO VERIFICAR OS PEDIDOS DE QUAL USUARIO PERTENCE

logger = logging.getLogger("app_webhook")  # Nome específico para o módulo de webhook

importar_pedidos = NuvemShop()


def processar_eventos(store_id, event_type, order_id):
    """
    Processar os eventos que estão sendo enviados pelo webhook para identificar cada processo para lidar com a situação
    """

    try:
        if event_type == "order/paid":
            return processar_pedido(store_id, order_id)
        elif event_type == "order/packed":
            return pedido_embalado(store_id, order_id)
        elif event_type == "order/fulfilled":
            return pedido_enviado(store_id, order_id)
        elif event_type == "order/cancelled":
            return pedido_cancelado(store_id, order_id)
        else:
            logger.warning("Tipo de evento desconhecido: %s", event_type)
            return False
    except Exception as e:
        logger.error("Erro ao processar evento: %s", e, exc_info=True)
        return False


def processar_pedido(store_id, order_id):
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        # Recuperar dados do pedido da Nuvem Shop
        novo_pedido = importar_pedidos._get_pedidos(
            code=token, store_id=store_id, id_pedido=order_id
        )
        logger.info("Pedido recuperado: %s", novo_pedido)

        # Verificar se o pedido já existe
        if Pedido.objects.filter(id_venda=f'#{novo_pedido["id"]}').exists():
            logger.info("Pedido já existe: %s", novo_pedido["id"])
            return False

        # Extrair dados do cliente do pedido
        cliente_dados = {
            "contact_name": novo_pedido.get("customer", {}).get("name", ""),
            "contact_email": novo_pedido.get("customer", {}).get("email", ""),
            "contact_identification": novo_pedido.get("customer", {}).get(
                "identification", ""
            ),
            "contact_phone": novo_pedido.get("customer", {}).get("phone", ""),
        }

        # Tentar obter o cliente existente (opcional)
        cliente, created = Cliente.objects.get_or_create(
            contact_email=cliente_dados["contact_email"], defaults=cliente_dados
        )

        # Processar o pedido utilizando o cliente recuperado ou criado
        novo_pedido_obj = Pedido.objects.create(
            cliente=cliente,
            loja=loja_integrada,
            id_pedido=novo_pedido["number"],
            id_venda=f'#{novo_pedido["id"]}',
            data_pedido=timezone.now(),
            total=novo_pedido["total"],
            status_pagamento="pago",
        )

        logger.info("Pedido processado com sucesso: %s", novo_pedido_obj)
        return True

    except LojaIntegrada.DoesNotExist:
        logger.error("Loja não encontrada: %s", store_id)
        return False
    except Exception as e:
        logger.error("Erro ao processar pedido: %s", e, exc_info=True)
        return False


def pedido_embalado(store_id, order_id):
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        # Recuperar dados do pedido da Nuvem Shop
        novo_pedido = importar_pedidos._get_pedidos(
            code=token, store_id=store_id, id_pedido=order_id
        )
        logger.info("Pedido recuperado para embalagem: %s", novo_pedido)

        pedido = Pedido.objects.get(id_venda=f'#{novo_pedido["id"]}')
        pedido.data_embalado = timezone.now()
        pedido.status_envio = "Embalado"
        pedido.save()

        logger.info("Pedido embalado com sucesso: %s", pedido)
        return True

    except (LojaIntegrada.DoesNotExist, ObjectDoesNotExist) as e:
        logger.error("Erro ao processar pedido embalado: %s", e, exc_info=True)
        return False
    except Exception as e:
        logger.error(
            "Erro inesperado ao processar pedido embalado: %s", e, exc_info=True
        )
        return False


def pedido_enviado(store_id, order_id):
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        # Recuperar dados do pedido da Nuvem Shop
        novo_pedido = importar_pedidos._get_pedidos(
            code=token, store_id=store_id, id_pedido=order_id
        )
        logger.info("Pedido recuperado para envio: %s", novo_pedido)

        pedido = Pedido.objects.get(id_venda=f'#{novo_pedido["id"]}')
        pedido.data_enviado = timezone.now()
        pedido.status_envio = "Enviado"
        pedido.codigo_rastreio = novo_pedido["shipping_tracking_number"]
        pedido.save()

        logger.info("Pedido enviado com sucesso: %s", pedido)
        return True

    except (LojaIntegrada.DoesNotExist, ObjectDoesNotExist) as e:
        logger.error("Erro ao processar pedido enviado: %s", e, exc_info=True)
        return False
    except Exception as e:
        logger.error(
            "Erro inesperado ao processar pedido enviado: %s", e, exc_info=True
        )
        return False


def pedido_cancelado(store_id, order_id):
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        # Recuperar dados do pedido da Nuvem Shop
        novo_pedido = importar_pedidos._get_pedidos(
            code=token, store_id=store_id, id_pedido=order_id
        )
        logger.info("Pedido recuperado para cancelamento: %s", novo_pedido)

        pedido = Pedido.objects.get(id_venda=f'#{novo_pedido["id"]}')
        pedido.status_pagamento = "cancelado"
        pedido.save()

        logger.info("Pedido cancelado com sucesso: %s", pedido)
        return True

    except (LojaIntegrada.DoesNotExist, ObjectDoesNotExist) as e:
        logger.error("Erro ao processar pedido cancelado: %s", e, exc_info=True)
        return False
    except Exception as e:
        logger.error(
            "Erro inesperado ao processar pedido cancelado: %s", e, exc_info=True
        )
        return False
