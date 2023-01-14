from django.urls import re_path
from .views import subscribe

urlpatterns = [
    re_path(r'^$', subscribe, name='subscribe')]
