from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from app_pedido.models import Cliente, Pedido
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import logging

from celery import shared_task

logger = logging.getLogger("app_webhook")  # Nome específico para o módulo de webhook

importar_pedidos = NuvemShop()


def formatar_numero(numero):
    if numero.startswith("+55"):
        return numero[3:]
    return numero


def recuperar_pedido(store_id, order_id):
    try:
        loja_integrada = LojaIntegrada.objects.get(id=store_id)
        token = loja_integrada.autorization_token

        # Tenta recuperar o pedido da API
        novo_pedido = importar_pedidos._get_pedidos(
            code=token, store_id=store_id, id_pedido=order_id
        )

        # Verifica se o pedido existe na resposta da API
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
    Processar os eventos que estão sendo enviados pelo webhook para identificar cada processo para lidar com a situação.

    store_id = Número da loja conectada
    event_type = Status do pedido
    order_id = Número do pedido com status pago
    """
    try:
        # Recupera os detalhes completos do pedido da API
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
    try:
        id_venda = f'#{novo_pedido["id"]}'

        # Verifica se o pedido já existe no banco de dados
        if not Pedido.objects.filter(id_venda=id_venda).exists():
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

            novo_pedido_obj = Pedido.objects.create(
                cliente=cliente,
                loja=LojaIntegrada.objects.get(id=store_id),
                id_pedido=novo_pedido["number"],
                id_venda=id_venda,
                data_pedido=timezone.now(),
                total=novo_pedido["total"],
                status_pagamento="pago",
                ultimo_status_notificado="Processando",
            )

            logger.info("Novo pedido criado com sucesso: %s", novo_pedido_obj)
            return True
        else:
            logger.info("Pedido já existe no banco de dados: %s", id_venda)
            return False

    except LojaIntegrada.DoesNotExist:
        logger.error("Loja não encontrada: %s", store_id)
        return False
    except Exception as e:
        logger.error("Erro ao processar pedido: %s", e, exc_info=True)
        return False


def atualizar_pedido(store_id, novo_pedido, status):
    try:
        id_venda = f'#{novo_pedido["id"]}'

        # Verifica se o pedido já existe no banco de dados
        pedido, created = Pedido.objects.get_or_create(
            id_venda=id_venda,
            defaults={
                "cliente": Cliente.objects.get_or_create(
                    contact_email=novo_pedido.get("customer", {}).get("email", ""),
                    defaults={
                        "contact_name": novo_pedido.get("customer", {}).get("name", ""),
                        "contact_email": novo_pedido.get("customer", {}).get(
                            "email", ""
                        ),
                        "contact_identification": novo_pedido.get("customer", {}).get(
                            "identification", ""
                        ),
                        "contact_phone": formatar_numero(
                            novo_pedido.get("customer", {}).get("phone", "")
                        ),
                    },
                )[0],
                "loja": LojaIntegrada.objects.get(id=store_id),
                "id_pedido": novo_pedido["number"],
                "data_pedido": timezone.now(),
                "total": novo_pedido["total"],
                "status_pagamento": "pago",
                "ultimo_status_notificado": "Processando",
            },
        )

        if created:
            logger.info("Novo pedido criado: %s", pedido)
        else:
            logger.info("Pedido existente atualizado: %s", pedido)

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

    except (LojaIntegrada.DoesNotExist, ObjectDoesNotExist) as e:
        logger.error("Erro ao processar pedido %s: %s", status, e, exc_info=True)
        return False
    except Exception as e:
        logger.error(
            "Erro inesperado ao processar pedido %s: %s", status, e, exc_info=True
        )
        return False
