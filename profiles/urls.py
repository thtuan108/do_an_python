from django.urls import re_path
from profiles.views import logout, login, register, create_profile, member_profile, delete, verification_message

urlpatterns = [
    re_path(r'^logout/', logout, name='logout'),
    re_path(r'^login/', login, name='login'),
    re_path(r'^register/', register, name='register'),
    re_path(r'^create-profile/', create_profile, name='create_profile'),
    re_path(r'^delete/', delete, name="delete"),
    re_path(r'^verification-message/', verification_message, name="verification_message"),
    re_path(r'^member/(?P<id>\d+)', member_profile, name='member_profile'),
]
