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
    if serializer.is_valid():
        user = serializer.save()

        if user.role.name == 'master':
            user.is_superuser = True
            user.is_staff = True
            user.save()
            logging.warning("Usuario master criado com sucesso: '%s'" % user.id)

        refresh = RefreshToken.for_user(user)

        logging.info("Usuario criado com sucesso no sistema: '%s'" % user.id)
        return Response({
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)

    logging.warning("Erro ao criar usuario'%s'" % list(serializer.errors.keys()))
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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