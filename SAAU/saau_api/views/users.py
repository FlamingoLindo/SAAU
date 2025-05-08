#listar e deletar
#importar em urls 
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import CustomUser
from ..serializer import UserSerializer, UserReadSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from ..permissions import IsStaffUser

import logging
import logging_config


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffUser])
@ratelimit(key='ip', rate='5/m', block=True)
def list_users(request):
    # Verifica se o usuário tem permissão (apenas masters podem listar todos)
    # def list_users(request):
    # users = CustomUser.objects.all()
    # serializer = UserSerializer(users, many=True)
    # logging.info("Usuário listou todos os usuários: '%s'" % request.user.id)
    # return Response(serializer.data, status=status.HTTP_200_OK)
    #if request.user.role.name != 'master':
        #logging.warning("Tentativa de listar usuários sem permissão: '%s'" % request.user.id)
       # return Response({"error": "Permissão negada."}, status=status.HTTP_403_FORBIDDEN)
    
    users = CustomUser.objects.all()
    serializer = UserReadSerializer(users, many=True)
    #logging.info("Usuário listou todos os usuários: '%s'" % request.user.id)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/m', block=True)
def delete_user(request, user_id):
    # Verifica se o usuário tem permissão (apenas masters ou o próprio usuário)
    if request.user.role.name != 'master' and request.user.id != user_id:
        logging.warning("Tentativa de deletar usuário sem permissão: '%s'" % request.user.id)
        return Response({"error": "Permissão negada."}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # Impede que um master seja deletado por outro usuário
        if user.role.name == 'master' and request.user.id != user_id:
            logging.warning("Tentativa de deletar master por outro usuário: '%s'" % request.user.id)
            return Response({"error": "Não é possível deletar um usuário master."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Marca como inativo em vez de deletar (soft delete)
        user.is_active = False
        user.save()
        logging.info("Usuário desativado: '%s' por '%s'" % (user_id, request.user.id))
        return Response({"message": "Usuário desativado com sucesso."}, status=status.HTTP_200_OK)
    
    except CustomUser.DoesNotExist:
        logging.warning("Tentativa de deletar usuário inexistente: '%s'" % user_id)
        return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/m', block=True)
def delete_account(request):
    user = request.user
    
    # Impede que um usuário master seja deletado (opcional)
    if user.role.name == 'master':
        logging.warning("Tentativa de deletar conta master: '%s'" % user.id)
        return Response({"error": "Não é possível deletar uma conta master."}, 
                        status=status.HTTP_403_FORBIDDEN)
    
    # Soft delete (marca como inativo)
    user.is_active = False
    user.save()
    
    logging.info("Usuário desativou sua própria conta: '%s'" % user.id)
    return Response({"message": "Conta desativada com sucesso."}, status=status.HTTP_200_OK)
