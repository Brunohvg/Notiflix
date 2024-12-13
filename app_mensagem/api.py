from ninja import Router
from .models import MensagemPadrao

router = Router()

@router.get('/')
def mensagems(request):
    return [{"Mensagem": e.mensagem_padrao} for e in MensagemPadrao.objects.all()]