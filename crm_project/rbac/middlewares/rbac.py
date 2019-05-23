#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/12
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, Http404
from django.conf import settings
import re


class RbacMiddleware(MiddlewareMixin):
    '''用户权限信息的校验'''

    def process_request(self, request):
        '''当用户请求进入时 触发执行'''
        '''
        1. 获取当前用户请求的url
        2. 获取当前用户在session中保存的 权限列表 [......]
        3. 当前请求url 在 session中， 就可以，进行访问
        '''

        current_url = request.path_info
        for valid_url in settings.VALID_URL_LIST:
            if re.match(valid_url, current_url):
                return None

        permission_dict = request.session.get(settings.PERMISSIONS_SESSION_KEY)  # 当前用户拥有的所有的权限信息
        if not permission_dict:
            '''用户未登录前 session为空, 所以直接返回就好了'''
            return HttpResponse("您没有访问权限...请登录")

        url_record = [{"title": "首页", "url": "#"}]
        for url in settings.NO_PERMISSION_LIST:
            if re.match(url, current_url):
                request.current_selected_permission = 0
                request.url_record = url_record
                # 这里不要单纯的返回数字！会在首次登录的时候，自定义的模板语法，会因为收到错误的数据而报错
                return None

        flag = False

        for item in permission_dict.values():
            reg = "^%s$" % item.get("url")

            if re.match(reg, current_url):
                flag = True
                request.current_selected_permission = item.get("paren_id") or item.get("id")
                if not item.get("paren_id"):
                    url_record.extend([{"title": item.get("title"), "url": item.get("url"), "class": "active"}])
                else:
                    url_record.extend([
                        {"title": item.get("paren_title"), "url": item.get("paren_url")},
                        {"title": item.get("title"), "url": item.get("url"), "class": "active"},
                    ])
                request.url_record = url_record
                break
        if not flag:
            return HttpResponse("无权访问")

