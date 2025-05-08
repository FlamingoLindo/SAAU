from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views.auth import MyTokenObtainPairView, create_user, login, reset_password
from .views.role import create_role

urlpatterns = [
    # Auth URLs
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login, name='login'),
    path('reset_password/', reset_password, name='reset_password'),

    # User URLs
    path('users/create/', create_user, name='create_user'),

    # Role URLs
    path('role/create/', create_role, name='create_role'),
] 