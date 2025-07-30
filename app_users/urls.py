from django.urls import path

from app_users.views import UsersView, UserOperationsView

app_name = 'app_users'

urlpatterns = [
    path('', UsersView.as_view(), name='users'),
    path('<str:user_id>/', UserOperationsView.as_view(), name='user_operations'),
]
