from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from app_pedido.models import Cliente, Pedido
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import logging

from celery import shared_task

logger = logging.getLogger("app_webhook")

importar_pedidos = NuvemShop()


def formatar_numero(numero):
    """Remove o código do país (+55) se presente."""
    if numero.startswith("+55"):
        return numero[3:]
    return numero


def recuperar_pedido(store_id, order_id):
    """Recupera um pedido da API NuvemShop usando o store_id e order_id."""
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        novo_pedido = importar_pedidos._get_pedidos(
            code=token, store_id=store_id, id_pedido=order_id
        )

        if not novo_pedido:
            logger.warning("Pedido não encontrado na API: %s", order_id)
            return None

        return novo_pedido

    except LojaIntegrada.DoesNotExist:
        logger.error("Loja não encontrada: %s", store_id)
        return None
    except Exception as e:
        logger.error("Erro ao recuperar pedido da API: %s", e, exc_info=True)
        return None


@shared_task(name="processar_eventos", max_retries=3, default_retry_delay=60)
def processar_eventos(store_id, event_type, order_id):
    """
    Processa eventos enviados pelo webhook e atualiza o pedido conforme o status.
    """
    try:
        novo_pedido = recuperar_pedido(store_id, order_id)

        if not novo_pedido:
            logger.error(
                "Não foi possível recuperar o pedido da API. Pedido não processado: %s",
                order_id,
            )
            return False

        if event_type == "order/paid":
            return processar_pedido(store_id, novo_pedido)
        elif event_type == "order/packed":
            return atualizar_pedido(store_id, novo_pedido, "embalado")
        elif event_type == "order/fulfilled":
            return atualizar_pedido(store_id, novo_pedido, "enviado")
        elif event_type == "order/cancelled":
            return atualizar_pedido(store_id, novo_pedido, "cancelado")
        else:
            logger.warning("Tipo de evento desconhecido: %s", event_type)
            return False

    except Exception as e:
        logger.error("Erro ao processar evento: %s", e, exc_info=True)
        return False


def processar_pedido(store_id, novo_pedido):
    """Processa o pedido e cria um novo cliente se o pedido for novo."""
    try:
        id_venda = f'#{novo_pedido.get("id", "desconhecido")}'

        if not Pedido.objects.filter(id_venda=id_venda).exists():
            return criar_novo_cliente(novo_pedido, id_venda, store_id)

        logger.info("Pedido já existe no banco de dados: %s", id_venda)
        return False

    except Exception as e:
        logger.error("Erro ao processar pedido: %s", e, exc_info=True)
        return False


def criar_novo_cliente(novo_pedido, id_venda, store_id):
    """Cria um novo cliente e pedido no banco de dados."""
    try:
        cliente_dados = {
            "contact_name": novo_pedido.get("customer", {}).get("name", ""),
            "contact_email": novo_pedido.get("customer", {}).get("email", ""),
            "contact_identification": novo_pedido.get("customer", {}).get(
                "identification", ""
            ),
            "contact_phone": formatar_numero(
                novo_pedido.get("customer", {}).get("phone", "")
            ),
        }
        cliente, created = Cliente.objects.get_or_create(
            contact_email=cliente_dados["contact_email"], defaults=cliente_dados
        )
        return criar_novo_pedido(cliente, novo_pedido, id_venda, store_id)
    except Exception as e:
        logger.error("Erro ao criar cliente: %s", e, exc_info=True)


def criar_novo_pedido(cliente, novo_pedido, id_venda, store_id):
    """Cria um novo pedido associado a um cliente."""
    try:
        novo_pedido_obj = Pedido.objects.create(
            cliente=cliente,
            loja=LojaIntegrada.objects.get(id=store_id),
            id_pedido=novo_pedido.get("number", "desconhecido"),
            id_venda=id_venda,
            data_pedido=timezone.now(),
            total=novo_pedido.get("total", 0),
            status_pagamento="pago",
            ultimo_status_notificado="Processando",
        )

        logger.info("Novo pedido criado com sucesso: %s", novo_pedido_obj)
        return True
    except Exception as e:
        logger.error("Erro ao criar novo pedido: %s", e, exc_info=True)
        return False


def atualizar_pedido(store_id, novo_pedido, status):
    """
    Atualiza um pedido existente ou cria um novo pedido se necessário.

    :param store_id: ID da loja integrada.
    :param novo_pedido: Dados do pedido a ser atualizado.
    :param status: Novo status do pedido.
    :return: Booleano indicando sucesso ou falha na atualização.
    """
    try:
        id_venda = f'#{novo_pedido.get("id", "desconhecido")}'

        # Obtém ou cria o cliente
        cliente = criar_novo_cliente(novo_pedido, id_venda, store_id)
        if not cliente:
            logger.error("Erro ao criar ou obter cliente para o pedido %s", id_venda)
            return False

        # Verifica se o pedido já existe no banco de dados
        pedido = Pedido.objects.filter(id_venda=id_venda).first()
        if pedido is None:
            # Se o pedido não existir, cria um novo
            criar_novo_pedido(cliente, novo_pedido, id_venda, store_id)
            pedido = Pedido.objects.get(id_venda=id_venda)

        # Atualiza o status do pedido
        status_map = {
            "embalado": ("Embalado", "embalado"),
            "enviado": ("Enviado", "enviado"),
            "cancelado": ("Devolvido", "cancelado"),
        }

        if status in status_map:
            status_envio, status_notificado = status_map[status]
            pedido.status_envio = status_envio
            pedido.ultimo_status_notificado = status_notificado

            if status == "embalado":
                pedido.data_embalado = timezone.now()
            elif status == "enviado":
                pedido.data_enviado = timezone.now()
                pedido.codigo_rastreio = novo_pedido.get("shipping_tracking_number", "")
            elif status == "cancelado":
                pedido.status_pagamento = "cancelado"

            pedido.save()
            logger.info("Pedido atualizado com sucesso: %s", pedido)
            return True
        else:
            logger.warning("Status desconhecido: %s", status)
            return False

    except LojaIntegrada.DoesNotExist:
        logger.error("Loja não encontrada: %s", store_id, exc_info=True)
        return False
    except Cliente.DoesNotExist:
        logger.error(
            "Cliente não encontrado para o email: %s",
            novo_pedido.get("customer", {}).get("email", ""),
            exc_info=True,
        )
        return False
    except ObjectDoesNotExist:
        logger.error(
            "Objeto não encontrado ao atualizar o pedido: %s", id_venda, exc_info=True
        )
        return False
    except Exception as e:
        logger.error(
            "Erro inesperado ao processar pedido %s: %s", status, e, exc_info=True
        )
        return False
