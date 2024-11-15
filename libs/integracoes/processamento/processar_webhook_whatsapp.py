from app_integracao.api.nuvemshop import NuvemShop
from app_integracao.models import LojaIntegrada
from app_pedido.models import Cliente, Pedido
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import logging
from datetime import datetime

logger = logging.getLogger("app_webhook")  # Nome específico para o módulo de webhook

importar_pedidos = NuvemShop()


def formatar_numero(numero):
    if numero.startswith("+55"):
        return numero[3:]
    return numero

def formatar_data(data_str):
    try:
        # Converte a string de data para um objeto datetime
        data = datetime.strptime(data_str, "%Y-%m-%dT%H:%M:%S%z")
        # Retorna apenas a parte da data no formato YYYY-MM-DD
        return data.date()  # Retorna como um objeto date
    except ValueError as e:
        logger.error("Erro ao formatar a data: %s", e)
        return None

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
            "contact_identification": novo_pedido.get("customer", {}).get("identification", ""),
            "contact_phone": formatar_numero(novo_pedido.get("customer", {}).get("phone", "")),
            "billing_name": novo_pedido.get("customer", {}).get("billing_name", ""),
            "total_spent": novo_pedido.get("customer", {}).get("total_spent", ""),
            "accepts_marketing": novo_pedido.get("customer", {}).get("accepts_marketing"),
            "last_order_id": novo_pedido.get("customer", {}).get("last_order_id"),
            
            # Campos de endereço integrado
            
            "billing_address": novo_pedido.get("customer", {}).get("billing_address", ""),
            "billing_number": novo_pedido.get("customer", {}).get("billing_number", ""),
            "billing_floor": novo_pedido.get("customer", {}).get("billing_floor", ""),
            "billing_locality": novo_pedido.get("customer", {}).get("billing_locality", ""),
            "billing_zipcode": novo_pedido.get("customer", {}).get("billing_zipcode", ""),
            "billing_city": novo_pedido.get("customer", {}).get("billing_city", ""),
            "billing_province": novo_pedido.get("customer", {}).get("billing_province", ""),
        }

        # Criando ou obtendo o cliente
        cliente, created = Cliente.objects.get_or_create(
            contact_email=cliente_dados["contact_email"], defaults=cliente_dados
        )

        # Atualizando os dados do cliente, se necessário
        if not created:
            for key, value in cliente_dados.items():
                setattr(cliente, key, value)
            cliente.save()

        novo_pedido_obj = Pedido.objects.create(
            cliente=cliente,
            loja=LojaIntegrada.objects.get(id=store_id),
            id_pedido=novo_pedido["number"],
            id_venda=f'#{novo_pedido["id"]}',
            data_pedido=novo_pedido['created_at'],
            total=novo_pedido["total"],
            status_pagamento="pago",
            ultimo_status_notificado="Processando",
            token_pedido = novo_pedido['token'],
            shipping_option_code=novo_pedido['shipping_option_code'],
            shipping_tracking_url=novo_pedido['shipping_tracking_url'],
            shipping_cost_customer=novo_pedido['shipping_cost_customer'],
            shipping_cost_owner=novo_pedido['shipping_cost_owner'],
            discount_coupon_code = novo_pedido.get("coupon", [])[0].get("code", "") if novo_pedido.get("coupon") else ""
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
                # TODO VERIFICAR A DATA DO PEDIDO
                "data_pedido": novo_pedido['created_at'],
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
                pedido.data_embalado = formatar_data(novo_pedido.get('updated_at'))
            elif status == "enviado":
                pedido.data_enviado = formatar_data(novo_pedido.get('shipped_at'))
                pedido.codigo_rastreio = novo_pedido.get("shipping_tracking_number", "")
                pedido.shipping_tracking_url = novo_pedido['shipping_tracking_url']
            elif status == "cancelado":
                pedido.status_pagamento = "cancelado"
                pedido.data_cancelado = formatar_data(novo_pedido.get('updated_at'))
                

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