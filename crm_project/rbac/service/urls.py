#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/15

from django.urls import reverse
from django.http import QueryDict

def memory_url(request, name, *args, **kwargs):
    '''
    生成带有原搜索条件的url  (?mid=1&age=20)  (替代原模板中的url)
    :param request:  # 从request中获取，当前请求的所有参数
    :param name:  # 帮助反向解析，生成url
    :return:
    '''
    basic_url = reverse(name, args=args, kwargs=kwargs)

    if not request.GET:
        return basic_url

    query_dict = QueryDict(mutable=True)
    query_dict["_filter"] = request.GET.urlencode()

    return "%s?%s" % (basic_url, query_dict.urlencode())


def memory_reverse(request, name, *args, **kwargs):
    '''
    反向生成url。
        1.在url获取原来的搜索条件， 如_filter之后的值
        2.reverse反向解析原来的url 如：/menu/list/
        3.进行拼接：/menu/list/?_filter=mid%3D2
    示例：
        http://127.0.0.1:8000/rbac/menu/add/?_filter=mid%3D2
    解析之后：
        http://127.0.0.1:8000/rbac/menu/list/?mid=2
    :param request:
    :param name:   # url的别名
    :param args:   # url中正则分组的位置参数
    :param kwargs: #url中正则分组的关键字参数
    :return:
    '''
    url = reverse(name, args=args, kwargs=kwargs)
    origin_params = request.GET.get("_filter")
    if origin_params:
        url = "%s?%s" % (url, origin_params)
    return url
