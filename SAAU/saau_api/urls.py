from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views.auth import MyTokenObtainPairView, create_user, login
from .views.role import create_role

urlpatterns = [
    # Auth URLs
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login, name='login'),

    # User URLs
    path('users/create/', create_user, name='create_user'),

    # Role URLs
    path('role/create/', create_role, name='create_role'),
] 