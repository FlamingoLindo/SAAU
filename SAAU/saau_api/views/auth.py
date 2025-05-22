from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import CustomUser
from ..serializer import UserSerializer, LoginSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import uuid
from sensitive_info.models import CPFToken, EmailToken, PhoneToken, BirthDateToken

import logging
import logging_config

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['name'] = user.name
        token['role'] = user.role.name

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@swagger_auto_schema(
    method='post',
    operation_summary="Criar novo usuário",
    request_body=UserSerializer,        
    responses={201: UserSerializer}     
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        logging.warning("Erro ao criar usuario: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 1) copie os dados validados
    data = serializer.validated_data.copy()

    #  pseudonimização do CPF
    cpf_real  = data.pop('document')
    cpf_token = uuid.uuid4()
    CPFToken.objects.using('sensitive').create(token=cpf_token, cpf_real=cpf_real)
    data['document'] = str(cpf_token)

    #  pseudonimização do E-mail
    email_real  = data.pop('email')
    email_token = uuid.uuid4()
    EmailToken.objects.using('sensitive').create(token=email_token, email_real=email_real)
    data['email'] = str(email_token)

    #  pseudonimização do Telefone
    phone_real  = data.pop('phone')
    phone_token = uuid.uuid4()
    PhoneToken.objects.using('sensitive').create(token=phone_token, phone_real=phone_real)
    data['phone'] = str(phone_token)

    #  pseudonimização da Data de Nascimento
    bd_real    = data.pop('birth_date')
    bd_token   = uuid.uuid4()
    BirthDateToken.objects.using('sensitive').create(token=bd_token, birth_date_real=bd_real)
    data['birth_date'] = str(bd_token)

    # 4) crie o usuário (fazendo set_password manualmente)
    password = data.pop('password')
    user = CustomUser(**data)
    user.set_password(password)
    user.save()

    # 5) trate superuser/staff se for master
    if user.role.name == 'master':
        user.is_superuser = True
        user.is_staff     = True
        user.save(update_fields=['is_superuser', 'is_staff'])
        logging.critical("Usuario master criado: %s", user.id)

    logging.info("Usuario criado com sucesso: %s", user.id)
    return Response({
        "user": UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='post',
    operation_summary="Login de usuário",
    request_body=LoginSerializer,
    responses={
        200: openapi.Response(
            description="Tokens + dados do usuário",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'access':  openapi.Schema(type=openapi.TYPE_STRING),
                    'user':    openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        401: "Credenciais incorretas",
        404: "Usuário não encontrado"
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def login(request):
    raw_email = request.data.get('email')
    password  = request.data.get('password')

    # 1) pega o token equivalente
    try:
        mapping = EmailToken.objects.using('sensitive').get(email_real=raw_email)
    except EmailToken.DoesNotExist:
        return Response({"error": "Usuário não encontrado."},
                        status=status.HTTP_404_NOT_FOUND)

    # 2) busca o CustomUser pelo token
    try:
        user = CustomUser.objects.get(email=str(mapping.token))
    except CustomUser.DoesNotExist:
        return Response({"error": "Usuário não encontrado."},
                        status=status.HTTP_404_NOT_FOUND)

    # 3) valida senha e ativa
    if not user.check_password(password):
        logging.warning("Tentativa de login com credenciais incorretas: %s", raw_email)
        return Response({"error": "Credenciais incorretas."},
                        status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({"error": "Conta desativada."},
                        status=status.HTTP_403_FORBIDDEN)

    # 4) login OK: atualiza last_login e emite tokens
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    refresh = RefreshToken.for_user(user)
    refresh['name'] = user.username
    refresh['role'] = user.role.name
    logging.info("Usuario logado com sucesso: %s", user.id)
    return Response({
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
        "user":    UserSerializer(user).data
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='put',
    operation_summary="Reset de senha do usuário logado",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'old_password':     openapi.Schema(type=openapi.TYPE_STRING),
            'new_password':     openapi.Schema(type=openapi.TYPE_STRING),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['old_password','new_password','confirm_password']
    ),
    responses={
        200: "Senha alterada com sucesso",
        400: "As senhas não coincidem",
        401: "Credenciais incorretas"
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/m', block=True)
def reset_password(request):
    user = request.user

    # 1) recupere o e-mail real a partir do token que está em user.email
    try:
        mapping = EmailToken.objects.using('sensitive').get(token=user.email)
    except EmailToken.DoesNotExist:
        return Response({"error": "Mapeamento de e-mail não encontrado."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    raw_email = mapping.email_real

    # 2) agora use user diretamente em vez de buscar por e-mail
    old_pw     = request.data.get('old_password')
    new_pw     = request.data.get('new_password')
    confirm_pw = request.data.get('confirm_password')

    # 3) confira a senha antiga
    if not user.check_password(old_pw):
        return Response({"error": "Credenciais incorretas."},
                        status=status.HTTP_401_UNAUTHORIZED)

    # 4) valide confirmação
    if new_pw != confirm_pw:
        return Response({"error": "As senhas não coincidem."},
                        status=status.HTTP_400_BAD_REQUEST)

    # 5) atualize a senha
    user.set_password(new_pw)
    user.save(update_fields=['password'])
    logging.info("Senha alterada para o e-mail %s (usuario %s)", raw_email, user.id)

    return Response({"message": "Senha alterada com sucesso."},
                    status=status.HTTP_200_OK)