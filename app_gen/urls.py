from django.urls import path

from app_gen.views import GenView

app_name = 'app_gen'

urlpatterns = [
    path('', GenView.as_view(), name='gen_view'),
]