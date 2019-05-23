#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/25
from django.conf import settings
from stark.servers.start_v1 import StartHandler


class PermissionHandler(object):
    # 是否显示添加按钮
    def get_add_btn(self, request, *args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSIONS_SESSION_KEY)  # 当前用户所有的权限信息
        url_name = "%s:%s" % (self.site.namespace, self.get_add_url_name)
        if url_name not in permission_dict:
            return None
        return super().get_add_btn(request, *args, **kwargs)  # 如果有权限，还执行原来的。添加函数就行

    # 是否显示，编辑和 添加按钮
    def get_list_display(self, request, *args, **kwargs):
        '''跟进权限，控制'''
        permission_dict = request.session.get(settings.PERMISSIONS_SESSION_KEY)
        value = []
        value.extend(self.list_display)
        if self.list_display:
            edit_name = "%s:%s" % (self.site.namespace, self.get_edit_url_name)
            del_name = "%s:%s" % (self.site.namespace, self.get_del_url_name)
            if edit_name in permission_dict and del_name in permission_dict:
                value.append(type(self).display_edit_and_display_del)
                return value
            elif edit_name in permission_dict:  # 当前用户是否有编辑权限
                value.append(type(self).display_edit)
            elif del_name in permission_dict:  # 当前用户是否有删除权限
                value.append(type(self).display_del)
        return value

