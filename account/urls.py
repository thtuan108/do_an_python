from django.urls import re_path
from .views import account

urlpatterns = [
    re_path(r'^$', account, name='account')
]
