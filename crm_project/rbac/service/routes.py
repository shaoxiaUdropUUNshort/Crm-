# ! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/16

import re
from collections import OrderedDict
from django.conf import settings
from django.utils.module_loading import import_string
from django.urls.resolvers import URLResolver, URLPattern


def get_all_url_dict():
    '''
    获取项目中，所有的url 保存到字典（前提是，每个url必须有name别名）
    :return:
    '''
    url_ordered_dict = OrderedDict()
    md = import_string(settings.ROOT_URLCONF)

    recursion_urls(None, "/", md.urlpatterns, url_ordered_dict)
    return url_ordered_dict


def recursion_urls(pre_namespace, pre_url, urlpatterns, url_ordered_dict):
    '''
    递归获取，所有的url
    :param pre_namespace:  namespace前缀，用于拼接name (namespace:name)
    :param pre_url:  url的前缀， 用于拼接url
    :param urlpatterns:  路由关系列表
    :param url_ordered_dict:  用于保存递归中获取的所有的路由
    :return:
    '''
    for item in urlpatterns:
        if isinstance(item, URLPattern):  # 表示一个 非路由分发。将路由添加到字典中
            if not item.name:  # 判断这个url 有没有，name别名
                continue

            name = item.name
            if pre_namespace:  # 判断当前这个url是不是有namespace前缀。也就是:是否是某一个命名空间中的 name别名
                name = "%s:%s" % (pre_namespace, item.name)

            url = (pre_url + str(item.pattern)).replace("^", "").replace("$", "")
            if check_url_exclude(url):
                continue
            url_ordered_dict[name] = {"name": name, "url": url}

        elif isinstance(item, URLResolver):  # 表示这是一个路由分发。 这里就需要递归了
            namespace = pre_namespace
            if pre_namespace:  # 如果有前缀
                if item.namespace:  # 自己有没有namespace
                    namespace = "%s:%s" % (pre_namespace, item.namespace)
            else:
                if item.namespace:
                    namespace = item.namespace

            recursion_urls(namespace, pre_url + str(item.pattern), item.url_patterns, url_ordered_dict)


def check_url_exclude(url):
    '''
    自定制，过滤一下。 以 xxx 为前缀的 url
    :param url:  需要检测的url
    :return:
    '''
    for regex in settings.AUTO_DISCOVER_EXCLUDE:
        if re.match(regex, url):
            return True





