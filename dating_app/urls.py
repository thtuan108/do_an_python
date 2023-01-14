"""dating_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path
from django.contrib import admin
from profiles import urls as profile_urls
from chat import urls as chat_urls
from home import urls as home_urls
from account import urls as account_urls
from checkout import urls as subscribe_urls
from search import urls as search_urls

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include(home_urls)),
    re_path(r'accounts/', include(profile_urls)),
    re_path(r'chat/', include(chat_urls)),
    re_path(r'subscribe/', include(subscribe_urls)),
    re_path(r'my-account/', include(account_urls)),
    re_path(r'search/', include(search_urls)),
    ]
