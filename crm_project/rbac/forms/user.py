#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/14

from django import forms
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from rbac import models
from rbac.forms.BASE import BootstrapModelForm


class UserInfoModelForm(BootstrapModelForm):
    '''
    用户 添加， form组件
    '''
    confirm_password = forms.CharField(label="确认密码")

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "confirm_password", "email"]
        # 手动的修改，显示什么样的错误信息
        # error_messages = {
        #     "name": {"required": "用户名不能为空"},
        #     "password": {"required": "密码不能为空"},
        #     "confirm_password": {"required": "确认密码不能为空"},
        #     "email": {"required": "邮箱不能为空"},
        # }

    # 然后是，样式的问题。 来个初始化方法。
    # def __init__(self, *args, **kwargs):
    #     super(UserInfoModelForm, self).__init__(*args, **kwargs)
    #     # 循环父类中生成的所有的字段，为每一个字段添加样式, 一次性为所有字典添加样式
    #     for name, field in self.fields.items():
    #         field.widget.attrs["class"] = "form-control"

    def clean_confirm_password(self):
        '''
        检测两次密码 是否一致
        :return:
        '''
        password = self.cleaned_data.get("password")
        confrim_password = self.cleaned_data.get("confirm_password")
        if password != confrim_password:
            raise ValidationError("两次密码输入不一致")
        return confrim_password


class UpdateUserInfoModelForm(BootstrapModelForm):
    '''
    修改用户时， 使用这个form组件
    '''

    class Meta:
        model = models.UserInfo
        fields = ["name", "email"]

    # def __init__(self, *args, **kwargs):
    #     super(UpdateUserInfoModelForm, self).__init__(*args, **kwargs)
    #     # 循环父类中生成的所有的字段，为每一个字段添加样式, 一次性为所有字典添加样式
    #     for name, field in self.fields.items():
    #         field.widget.attrs["class"] = "form-control"


class ResetPasswordUserInfoModelForm(BootstrapModelForm):
    '''重置密码的工作'''
    confirm_password = forms.CharField(label="确认密码")

    class Meta:
        model = models.UserInfo
        fields = ["password", "confirm_password"]

    # def __init__(self, *args, **kwargs):
    #     super(ResetPasswordUserInfoModelForm, self).__init__(*args, **kwargs)
    #     # 循环父类中生成的所有的字段，为每一个字段添加样式, 一次性为所有字典添加样式
    #     for name, field in self.fields.items():
    #         field.widget.attrs["class"] = "form-control"

    def clean_confirm_password(self):
        '''
        检测两次密码 是否一致
        :return:
        '''
        password = self.cleaned_data.get("password")
        confrim_password = self.cleaned_data.get("confirm_password")
        if password != confrim_password:
            raise ValidationError("两次密码输入不一致")
        return confrim_password


