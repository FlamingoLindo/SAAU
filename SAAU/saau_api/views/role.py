from rest_framework.decorators import api_view, permission_classes
from ..permissions import IsStaffUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializer import RoleSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_summary="Criar nova role",
    request_body=RoleSerializer,
    responses={201: RoleSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffUser])
def create_role(request):
    serializer = RoleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)