from ninja import Router, ModelSchema
from .models import Profile
from django.core.exceptions import ObjectDoesNotExist

router = Router()

class ProfileModelSchema(ModelSchema):
    class Meta:
        model = Profile
        fields = ['id', 'nome', 'whatsapp', 'notificacao_whatsapp', 'notificacao_email']

def paginate(queryset, page: int, page_size: int):
    """
    Pagina um queryset.
    """
    if page < 1 or page_size < 1:
        raise ValueError("Page and page_size must be greater than 0.")
    start = (page - 1) * page_size
    end = start + page_size
    return queryset[start:end]

@router.get("/", response=list[ProfileModelSchema])
def list_profile(request, page: int = 1, page_size: int = 10):
    """
    Lista todos os perfis com paginação.

    Args:
        request: O objeto da requisição.
        page: Número da página (padrão é 1).
        page_size: Número de perfis por página (padrão é 10).

    Returns:
        Uma lista de perfis paginada.
    """
    try:
        profiles = paginate(Profile.objects.all(), page, page_size)
        return [ProfileModelSchema.from_orm(profile) for profile in profiles]
    except ValueError as e:
        return {"error": str(e)}, 400

@router.get("/{profile_id}", response=ProfileModelSchema)
def profile_details(request, profile_id: int):
    """
    Obtém os detalhes de um perfil específico.

    Args:
        request: O objeto da requisição.
        profile_id: ID do perfil a ser buscado.

    Returns:
        Detalhes do perfil ou um erro 404 se não encontrado.
    """
    try:
        profile = Profile.objects.get(id=profile_id)
        return ProfileModelSchema.from_orm(profile)
    except ObjectDoesNotExist:
        return {"error": "Profile not found"}, 404
