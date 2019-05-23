#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/14
"""crm_learn URL Configuration

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
from django.urls import path,include,re_path
from rbac.views import role, user, menu

urlpatterns = [
    re_path(r"^role/list/$", role.role_list, name="role_list"),
    re_path(r"^role/add/$", role.role_add, name="role_add"),
    re_path(r"^role/edit/(?P<pk>\d+)/$", role.role_edit, name="role_edit"),
    re_path(r"^role/del/(?P<pk>\d+)/$", role.role_del, name="role_del"),

    # re_path(r"^user/list/$", user.user_list, name="user_list"),
    # re_path(r"^user/add/$", user.user_add, name="user_add"),
    # re_path(r"^user/edit/(?P<pk>\d+)/$", user.user_edit, name="user_edit"),
    # re_path(r"^user/del/(?P<pk>\d+)/$", user.user_del, name="user_del"),

    # re_path(r"^user/reset/password/(?P<pk>\d+)/$", user.reset_pwd, name="reset_pwd"),

    re_path("^menu/list/$", menu.menu_list, name="menu_list"),
    re_path("^menu/add/$", menu.menu_add, name="menu_add"),
    re_path(r"^menu/edit/(?P<pk>\d+)/$", menu.menu_edit, name="menu_edit"),
    re_path(r"^menu/del/(?P<pk>\d+)/$", menu.menu_del, name="menu_del"),

    re_path(r"^second/menu/add/(?P<menu_id>\d+)/$", menu.second_menu_add, name="second_menu_add"),
    re_path(r"^second/menu/edit/(?P<pk>\d+)/$", menu.second_menu_edit, name="second_menu_edit"),
    re_path(r"^second/menu/del/(?P<pk>\d+)/$", menu.second_menu_del, name="second_menu_del"),

    re_path(r"^permission/add/(?P<second_menu_id>\d+)/$", menu.permission_add, name="permission_add"),
    re_path(r"^permission/edit/(?P<pk>\d+)/$", menu.permission_edit, name="permission_edit"),
    re_path(r"^permission/del/(?P<pk>\d+)/$", menu.permission_del, name="permission_del"),

    # 批量操作权限
    re_path(r"^multi/permissions/$", menu.multi_permissions, name="multi_permissions"),
    re_path(r"^multi/permissions/del/(?P<pk>\d+)/$", menu.multi_permissions_del, name="multi_permissions_del"),

    # 批量分配权限
    re_path(r"^distribute/permissions/$", menu.distribute_permission, name="distribute_permission"),
]