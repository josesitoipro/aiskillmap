from django.urls import path

from app_auth.views import LoginView, LogoutView, RefreshTokenView

app_name = 'app_auth'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh_token'),
]
