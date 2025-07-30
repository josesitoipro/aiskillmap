from django.urls import path, include

urlpatterns = [
    path('', include('core.urls')),
    path('v1/api/auth/', include('app_auth.urls', namespace='app_auth')),
    path('v1/api/users/', include('app_users.urls', namespace='app_users')),
    path('v1/api/generation/', include('app_gen.urls', namespace='app_gen')),
]
