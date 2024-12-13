from ninja import Router
from .models import Pedido

router = Router()

@router.get("/")
def list_orders(request):
    return [{"loja": e.loja, "id_venda": e.id_venda} for e in Pedido.objects.all()]


@router.get("/{order_id}")
def order_details(request, order_id: int):
    order = Pedido.objects.get(id=order_id)
    return {"cliente": order.cliente.contact_name , "rastreio": order.codigo_rastreio }
