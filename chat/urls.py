from django.urls import re_path
from chat.views import chat, new_message_check, wink, chat_ajax, chat_home, read_messages, winks, read_wink, read_view, views

urlpatterns = [
    re_path(r'^(?P<id>\d+)', chat, name="chat"),
    re_path(r'^home/', chat_home, name="chat_home"),
    re_path(r'^ajax/winks/$', wink, name="wink"),
    re_path(r'^ajax/new_message_check/$', new_message_check, name='new_message_check'),
    re_path(r'^ajax/read/$', read_messages, name="read_messages"),
    re_path(r'^ajax/new_message/$', chat_ajax, name="new_message"),
    re_path(r'^winks/$', winks, name="winks"),
    re_path(r'^views/$', views, name="views"),
    re_path(r'^ajax/read-view/', read_view, name='read_view'),
    re_path(r'^ajax/read-wink/', read_wink, name='read_wink'),
]