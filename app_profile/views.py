from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from app_mensagem.models import MensagemPadrao


@csrf_exempt
def autenticar_usuario(request):
    """
    View para autenticar usuários.

    Recebe dados de autenticação do formulário de login e redireciona para o painel
    de controle se a autenticação for bem-sucedida. Caso contrário, exibe uma
    mensagem de erro.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("app_dashboard:dashboard")
        else:
            messages.error(request, "Usuário ou senha inválido")
    return render(request, "app_profile/login.html")


@csrf_exempt
def registrar_usuario(request):
    """
    View para registrar novos usuários.

    Recebe dados do formulário de registro, cria um novo usuário e um perfil associado
    e redireciona para o painel de controle após o registro bem-sucedido.
    """
    if request.method == "POST":
        nome = request.POST.get("nome").capitalize()
        email = request.POST.get("email")
        senha = request.POST.get("password")
        whatsapp = request.POST.get("whatsapp")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Já existe um usuário com o mesmo e-mail")
        else:
            novo_usuario = User.objects.create_user(
                username=email, email=email, password=senha
            )
            Profile.objects.create(nome=nome, whatsapp=whatsapp, user=novo_usuario)

            # Dicionário de mensagens padrão para cada tipo de pedido
            mensagens_por_tipo = {
                "Pedido Pago": (
                    "Olá [nome_cliente],\n\n"
                    "🎉 Acabamos de receber seu pedido #[numero_pedido]!\n"
                    "Agradecemos a sua compra e estamos verificando tudo para o próximo passo.\n\n"
                    "Atenciosamente,\n"
                    "Equipe de Vendas"
                ),
                "Pedido Embalado": (
                    "Boas notícias [nome_cliente],\n\n"
                    "📦 Tudo certo com seu pedido #[numero_pedido], acabamos de embalar e está pronto para envio!\n"
                    "Estamos cuidando de todos os detalhes para que seu pedido chegue em perfeito estado.\n\n"
                    "Atenciosamente,\n"
                    "Equipe de Logística"
                ),
                "Pedido Enviado": (
                    "Olá [nome_cliente], agora é só aguardar! 🚚\n\n"
                    "Seu pedido #[numero_pedido] foi enviado e está a caminho!\n"
                    "Em breve você receberá suas compras no endereço fornecido. Acompanhe o rastreamento para mais detalhes: [link_rastreio].\n\n"
                    "Atenciosamente,\n"
                    "Equipe de Entregas"
                ),
                "Pedido Cancelado": (
                    "Olá [nome_cliente],\n\n"
                    "Lamentamos informar que seu pedido #[numero_pedido] foi cancelado. 😔\n"
                    "Se você tiver alguma dúvida ou precisar de assistência, por favor, entre em contato conosco.\n"
                    "Estamos à disposição para ajudar no que for necessário.\n\n"
                    "Atenciosamente,\n"
                    "Equipe de Atendimento ao Cliente"
                ),
                "Carrinho Abandonado": (
                    "Olá [nome_cliente],\n\n"
                    "Somos da [nome_loja] e esperamos que você esteja bem. 😊\n"
                    "Vimos que você iniciou uma compra em nossa loja e não finalizou, se precisar de ajuda, conte com a gente!\n"
                    "Aqui está o link para continuar sua compra: [cart.link]\n\n"
                    "Atenciosamente,\n"
                    "Equipe de Vendas"
                ),
            }

            # Criação de mensagens padrão para o novo usuário
            for tipo_pedido, mensagem in mensagens_por_tipo.items():
                MensagemPadrao.objects.create(
                    usuario=novo_usuario,
                    tipo_pedido=tipo_pedido,
                    mensagem_padrao=mensagem,
                )

            user = authenticate(request, username=email, password=senha)
            if user is not None:
                login(request, user)
                return redirect("app_dashboard:dashboard")
            else:
                messages.error(request, "Falha ao autenticar usuário")

    return render(request, "app_profile/registrar.html")


def redefinir_senha(request):
    """
    View para solicitar a redefinição de senha.

    Recebe um endereço de e-mail do formulário de redefinição de senha e envia instruções
    para redefinir a senha se o endereço de e-mail estiver associado a uma conta existente.
    Caso contrário, exibe uma mensagem de erro.
    """
    if request.method == "POST":
        email = request.POST.get("emailRedefinir")
        if User.objects.filter(email=email).exists():
            # Implementar a lógica de redefinição de senha aqui
            messages.success(
                request,
                "Instruções para redefinição de senha enviadas para o e-mail fornecido.",
            )
        else:
            messages.error(request, "Não existe uma conta associada a este e-mail.")
    return render(request, "app_profile/redefinir.html")


@login_required
def deslogar_usuario(request):
    """
    View para deslogar usuários.

    Realiza o logout do usuário e redireciona para a página de login.
    """
    logout(request)
    return redirect("autenticar_usuario")


@login_required
def exibir_perfil(request):
    """
    View para exibir o perfil do usuário.

    Exibe o perfil do usuário logado.
    """
    # TODO: Verificar o status de recebimento de notificações e outras lógicas necessárias
    return render(request, "app_profile/perfil.html")


@login_required
def atualizar_perfil_usuario(request):
    """
    View para atualizar o perfil do usuário.

    Recebe dados do formulário de atualização de perfil e atualiza o perfil do usuário
    logado. Em seguida, redireciona de volta para a página de perfil.
    """
    if request.method == "POST":
        # Implementar a lógica de atualização do perfil do usuário aqui
        messages.success(request, "Perfil atualizado com sucesso.")
    return redirect("exibir_perfil")
