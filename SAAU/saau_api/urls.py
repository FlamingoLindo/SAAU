from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views.auth import MyTokenObtainPairView, create_user, login, reset_password
from .views.role import create_role
from .views.users import list_users, delete_user, delete_account, get_user, change_user_status

urlpatterns = [
    # Auth URLs
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login, name='login'),
    path('reset_password/', reset_password, name='reset_password'),

    # User URLs
    path('users/create/', create_user, name='create_user'),
    path('users/listUser/', list_users, name='list_users'),
    path('users/deleteUser/<int:user_id>/', delete_user, name='delete_user'),
    path('users/delete_account/', delete_account, name='delete_account'),
    path('users/<int:user_id>/', get_user, name='get_user'),
    path('users/<int:pk>/toggle-active/', change_user_status, name='change-user-status'),

    # Role URLs
    path('role/create/', create_role, name='create_role'),

] 