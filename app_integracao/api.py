from ninja import Router
from .models import LojaIntegrada

router = Router()

@router.get("/")
def list_loja(request):
    return [{"id": e.pk, "nome": e.nome} for e in LojaIntegrada.objects.all()]

@router.get('/{loja_id}')  # Altere o nome da rota para 'loja_id'
def loja_details(request, loja_id: int):  # Altere o nome do parâmetro para 'loja_id'
    loja = LojaIntegrada.objects.get(id=loja_id)  # Use 'loja_id' para buscar a loja
    return {"nome": loja.nome}