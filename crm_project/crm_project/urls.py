"""crm_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from stark.servers.start_v1 import site
from web.views import account
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('^stark/', site.urls),
    re_path(r'^rbac/', include(('rbac.urls', 'rbac'))),
    path("login/", account.login, name="login"),
    path("logout/", account.logout, name="logout"),
    path("index/", account.index, name="index"),
]

# if settings.DEBUG:
#     urlpatterns += static()
