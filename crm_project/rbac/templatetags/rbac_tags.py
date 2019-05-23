#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/12
from django.template import Library
from django.conf import settings
import re
from collections import OrderedDict
from django.urls import reverse
from django.http import QueryDict
from rbac.service import urls

register = Library()


@register.inclusion_tag("rbac/static_menu.html")
def static_menu(request):
    '''
    创建一级菜单
    :return:
    '''
    path_info = request.path_info
    menu_list = request.session.get(settings.MENU_SESSION_KEY)
    return {"menu_list": menu_list, "path_info": path_info}


@register.inclusion_tag("rbac/multi_menu.html")
def multi_menu(request):
    '''
    创建二级菜单
    :return:
    '''
    current_selected_permission = request.current_selected_permission
    menu_dict = request.session.get(settings.MENU_SESSION_KEY)

    key_list = sorted(menu_dict)  # 对字典的key 进行排序
    ordered_dict = OrderedDict()  # 创建一个空的 有序字典
    for key in key_list:  # 循环有序字典列表
        val = menu_dict[key]  # 得到每一个字典
        val["class"] = "hide"  # 添加一个 class:hide 键值. 控制标签的显示隐藏. 默认全部添加，下面代码进行选择性覆盖
        for per in val["children"]:  # 循环 当前字典(菜单) 下的 子菜单
            if per.get("id") == current_selected_permission:
                per["class"] = "active"  # 匹配成功 为当前子菜单添加  class:active 类属性(表示被选中的)
                val["class"] = ""  # 当前一级菜单的 class:""  跟改为空， 覆盖掉hide（不隐藏）
        ordered_dict[key] = val  # 最终将设置好的每一个字典。 添加到有序字典当中
    return {"ordered_dict": ordered_dict}


@register.inclusion_tag("rbac/url_record.html")
def url_record(request):
    return {"record_list": request.url_record}


@register.filter
def has_permission(request, name):
    '''
    :param request:  request对象
    :param name:   当前权限的别名
    :return:
    '''
    if name in request.session.get(settings.PERMISSIONS_SESSION_KEY):
        return True


@register.simple_tag
def memory_url(request, name, *args, **kwargs):
    '''
    生成带有原搜索条件的url  (?mid=1&age=20)  (替代原模板中的url)
    :param request:  # 从request中获取，当前请求的所有参数
    :param name:  # 帮助反向解析，生成url
    :return:
    '''
    return urls.memory_url(request, name, *args, **kwargs)
