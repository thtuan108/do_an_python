from django.urls import re_path
from .views import index, preregister

urlpatterns = [
    re_path(r'^$', preregister, name='preregister'),
    re_path(r'^home/', index, name="index"),
]
