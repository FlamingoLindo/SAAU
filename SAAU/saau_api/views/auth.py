from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import CustomUser
from ..serializer import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes

import uuid
from sensitive_info.models import CPFToken

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

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        logging.warning("Erro ao criar usuário: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 1) copie os dados validados
    data = serializer.validated_data.copy()

    # 2) retire o CPF real e gere o token
    cpf_real = data.pop('document')
    token = uuid.uuid4()
    CPFToken.objects.using('sensitive').create(
        token=token,
        cpf_real=cpf_real
    )

    # 3) substitua no dict pelo token
    data['document'] = str(token)

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
        logging.critical("Usuário master criado: %s", user.id)

    # 6) emita o JWT e retorne
    refresh = RefreshToken.for_user(user)
    logging.info("Usuário criado com sucesso: %s", user.id)
    return Response({
        "user": UserSerializer(user).data,
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def login(request):
    try:
        user = CustomUser.objects.get(email=request.data['email'])
    except CustomUser.DoesNotExist:
        logging.warning("Erro ao fazer login: '%s'" % user.id)
        return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if user.check_password(request.data['password']):
        if not user.is_active:
            logging.warning("Tentativa de login com conta desativada: '%s'" % user.id)
            return Response({"error": "Conta desativada."}, status=status.HTTP_403_FORBIDDEN)
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        refresh = RefreshToken.for_user(user)
        logging.warning("Usuario logado com sucesso no sistema: '%s'" % user.id)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
        
    logging.warning("Tentativa de fazer login com credencias incorretas: '%s'" % user.id)
    return Response({"error": "Credenciais incorretas."}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/m', block=True)
def reset_password(request):
    id = request.user.id
    try:
        user = CustomUser.objects.get(email=request.data['email'])
    except CustomUser.DoesNotExist:
        logging.warning("Erro ao fazer reset de senha: '%s'" % id)
        return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if user.check_password(request.data['old_password']):
        if request.data['new_password'] != request.data['confirm_password']:
            logging.warning("Tentativa de fazer reset de senha com senhas diferentes: '%s'" % user.id)
            return Response({"error": "As senhas não coincidem."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(request.data['new_password'])
        user.save()
        logging.info("Senha alterada com sucesso: '%s'" % user.id)
        return Response({"message": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)

    logging.warning("Tentativa de fazer reset de senha com credencias incorretas: '%s'" % user.id)
    return Response({"error": "Credenciais incorretas."}, status=status.HTTP_401_UNAUTHORIZED)