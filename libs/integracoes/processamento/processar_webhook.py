#from app_integracao.api_teste.nuvemshop import NuvemShop
from libs.integracoes.api.api_nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from app_pedido.models import Cliente, Pedido
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger("app_webhook")  # Nome específico para o módulo de webhook

importar_pedidos = NuvemShop()


def formatar_numero(numero):
    if numero.startswith("+55"):
        return numero[3:]
    return numero


def processar_eventos(store_id, event_type, order_id):
    """
    Processar os eventos que estão sendo enviados pelo webhook para identificar cada processo para lidar com a situação.

    store_id = Numero da loja conecta
    event_type = Status do pedido
    order_id = Numero do pedido com status pago
    """
    try:
        if event_type == "order/paid":
            return processar_pedido(store_id, order_id)
        elif event_type == "order/packed":
            return atualizar_pedido(store_id, order_id, "embalado")
        elif event_type == "order/fulfilled":
            return atualizar_pedido(store_id, order_id, "enviado")
        elif event_type == "order/cancelled":
            return atualizar_pedido(store_id, order_id, "cancelado")
        else:
            logger.warning("Tipo de evento desconhecido: %s", event_type)
            return False
    except Exception as e:
        logger.error("Erro ao processar evento: %s", e, exc_info=True)
        return False


def recuperar_pedido(store_id, order_id):
    loja_integrada = LojaIntegrada.objects.get(id=store_id)
    token = loja_integrada.autorization_token
    return importar_pedidos._get_pedidos(
        code=token, store_id=store_id, id_pedido=order_id
    )


def processar_pedido(store_id, order_id):
    try:
        novo_pedido = recuperar_pedido(store_id, order_id)
        logger.info("Pedido recuperado: %s", novo_pedido)

        if Pedido.objects.filter(id_venda=f'#{novo_pedido["id"]}').exists():
            logger.info("Pedido já existe: %s", novo_pedido["id"])
            return False

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
            id_venda=f'#{novo_pedido["id"]}',
            data_pedido=timezone.now(),
            total=novo_pedido["total"],
            status_pagamento="pago",
            ultimo_status_notificado="Processando",
            token_pedido = novo_pedido['token'],
            
        )

        logger.info("Pedido processado com sucesso: %s", novo_pedido_obj)
        return True

    except LojaIntegrada.DoesNotExist:
        logger.error("Loja não encontrada: %s", store_id)
        return False
    except Exception as e:
        logger.error("Erro ao processar pedido: %s", e, exc_info=True)
        return False


def atualizar_pedido(store_id, order_id, status):
    try:
        novo_pedido = recuperar_pedido(store_id, order_id)
        logger.info("Pedido recuperado para atualização: %s", novo_pedido)

        pedido, created = Pedido.objects.get_or_create(
            id_venda=f'#{novo_pedido["id"]}',
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
                        "contact_phone": novo_pedido.get("customer", {}).get(
                            "phone", ""
                        ),
                    },
                )[0],
                "loja": LojaIntegrada.objects.get(id=store_id),
                "id_pedido": novo_pedido["number"],
                "data_pedido": timezone.now(),
                "total": novo_pedido["total"],
                "status_pagamento": "pago",
            },
        )

        if created:
            logger.info("Novo pedido criado: %s", pedido)
        else:
            logger.info("Pedido já existente atualizado: %s", pedido)

        status_map = {
            "embalado": ("Embalado", "embalado"),
            "enviado": ("Enviado", "enviado"),
            "cancelado": ("Devolvido", "cancelado"),
        }

        if status in status_map:
            print(status)
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
            logger.info("Pedido %s com sucesso: %s", status, pedido)
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


"""def atualizar_pedido(store_id, order_id, status):
    try:
        novo_pedido = recuperar_pedido(store_id, order_id)
        logger.info("Pedido recuperado para atualização: %s", novo_pedido)

        pedido, created = Pedido.objects.get_or_create(
            id_venda=f'#{novo_pedido["id"]}',
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
                        "contact_phone": novo_pedido.get("customer", {}).get(
                            "phone", ""
                        ),
                    },
                )[0],
                "loja": LojaIntegrada.objects.get(id=store_id),
                "id_pedido": novo_pedido["number"],
                "data_pedido": timezone.now(),
                "total": novo_pedido["total"],
                "status_pagamento": "pago",
            },
        )

        if created:
            logger.info("Novo pedido criado: %s", pedido)
        else:
            logger.info("Pedido já existente atualizado: %s", pedido)

        if status == "embalado":
            pedido.data_embalado = timezone.now()
            pedido.status_envio = "Embalado"
            pedido.ultimo_status_notificado = 'Embalado'
        elif status == "enviado":
            pedido.data_enviado = timezone.now()
            pedido.status_envio = "Enviado"
            pedido.ultimo_status_notificado = 'Enviado'
            pedido.codigo_rastreio = novo_pedido.get("shipping_tracking_number", "")
        elif status == "cancelado":
            pedido.status_pagamento = "cancelado"
            pedido.ultimo_status_notificado = 'Devolvido'
            pedido.status_envio = "Devolvido"
        pedido.save()

        logger.info("Pedido %s com sucesso: %s", status, pedido)
        return True

    except (LojaIntegrada.DoesNotExist, ObjectDoesNotExist) as e:
        logger.error("Erro ao processar pedido %s: %s", status, e, exc_info=True)
        return False
    except Exception as e:
        logger.error(
            "Erro inesperado ao processar pedido %s: %s", status, e, exc_info=True
        )
        return False"""
