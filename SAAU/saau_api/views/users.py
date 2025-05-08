#listar e deletar
#importar em urls 
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from ..permissions import IsStaffUser
from ..models import CustomUser
from ..serializer import UserReadSerializer
from sensitive_info.models import CPFToken, EmailToken, PhoneToken, BirthDateToken

import logging
import logging_config

# LISTAGEM DE USUÁRIO (MÁSCARA)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffUser])
@ratelimit(key='ip', rate='5/m', block=True)
def list_users(request):

    users = CustomUser.objects.all()
    serializer = UserReadSerializer(users, many=True)
    logging.info("Todos os usuarios listados por: '%s'" % request.user.id)
    return Response(serializer.data, status=status.HTTP_200_OK)

# DELETAR UM USUÁRIO ESCOLHIDO
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/m', block=True)
def delete_user(request, user_id):
    # Verifica se o usuário tem permissão (apenas masters ou o próprio usuário)
    if request.user.role.name != 'master' and request.user.id != user_id:
        logging.warning("Tentativa de deletar usuario sem permissao: '%s'" % request.user.id)
        return Response({"error": "Permissão negada."}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # Impede que um master seja deletado por outro usuário
        if user.role.name == 'master' and request.user.id != user_id:
            logging.critical("Tentativa de deletar master por outro usuario: '%s'" % request.user.id)
            return Response({"error": "Não é possível deletar um usuário master."}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Apaga os dados "irmãos" do BD sensivel
        CPFToken.objects.using('sensitive') \
        .filter(token=user.document).delete()
        EmailToken.objects.using('sensitive') \
            .filter(token=user.email).delete()
        PhoneToken.objects.using('sensitive') \
            .filter(token=user.phone).delete()
        BirthDateToken.objects.using('sensitive') \
            .filter(token=user.birth_date).delete()
        
        user.delete()
        logging.info("Usuario deletado: '%s' por '%s'" % (user_id, request.user.id))
        return Response({"message": "Usuário deletado com sucesso."}, status=status.HTTP_204_NO_CONTENT)
    
    except CustomUser.DoesNotExist:
        logging.warning("Tentativa de deletar usuario inexistente: '%s'" % user_id)
        return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

# DELETAR CONTA DE USUÁRIO LOGADO
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/m', block=True)
def delete_account(request):
    user = request.user

    # Master não pode se deletar
    if user.role.name == 'master':
        logging.warning("Tentativa de deletar conta master: %s", user.id)
        return Response(
            {"error": "Não é possível deletar uma conta master."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Invalida token
    try:
        refresh_token = request.data.get('refresh')  
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass

    # Apaga os dados "irmãos" do BD sensivel
    CPFToken.objects.using('sensitive') \
        .filter(token=user.document).delete()
    EmailToken.objects.using('sensitive') \
        .filter(token=user.email).delete()
    PhoneToken.objects.using('sensitive') \
        .filter(token=user.phone).delete()
    BirthDateToken.objects.using('sensitive') \
        .filter(token=user.birth_date).delete()

    # 5) apagar o próprio usuário do DB default
    user.delete()
    logging.info("Usuario excluiu sua propria conta: %s", user.id)

    # 6) retornar sem conteúdo
    return Response(status=status.HTTP_204_NO_CONTENT)
