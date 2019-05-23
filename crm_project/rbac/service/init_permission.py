#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/12
from django.conf import settings


def init_permission(current_user, request):
    '''  二级菜单，实现
    :param current_user: 当前请求 用户对象
    :param request:  当前请求 数据
    :return:
    '''

    permission_queryset = current_user.roles.filter(permissions__isnull=False) \
        .values("permissions__id", "permissions__url", "permissions__title", "permissions__name",
                "permissions__pid_id", "permissions__pid__title", "permissions__pid__url",
                "permissions__menu_id", "permissions__menu__icon", "permissions__menu__title", ).distinct()

    menu_dict = {}
    permission_dict = {}
    for item in permission_queryset:
        permission_dict[item.get("permissions__name")] = {
            "id": item.get("permissions__id"),
            "title": item.get("permissions__title"),
            "url": item.get("permissions__url"),
            "paren_id": item.get("permissions__pid_id"),
            "paren_title": item.get("permissions__pid__title"),
            "paren_url": item.get("permissions__pid__url"),
        }

        menu_id = item.get("permissions__menu_id")
        if not menu_id:
            continue

        node = {"id": item.get("permissions__id"), "title": item.get("permissions__title"),
                "url": item.get("permissions__url")}
        if menu_id in menu_dict:
            menu_dict[menu_id]["children"].append(node)
        else:
            menu_dict[menu_id] = {
                "title": item.get("permissions__menu__title"),
                "icon": item.get("permissions__menu__icon"),
                "children": [node]
            }
    request.session[settings.PERMISSIONS_SESSION_KEY] = permission_dict
    request.session[settings.MENU_SESSION_KEY] = menu_dict
