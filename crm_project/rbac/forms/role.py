#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/14

from django import forms
from django.core.exceptions import ValidationError,NON_FIELD_ERRORS
from rbac import models
from rbac.forms.BASE import BootstrapModelForm

class RolemodelForm(forms.ModelForm):
    '''
    角色 添加， fomr 组件
    '''

    class Meta:
        model = models.Role
        fields = ["title"]  # fields = "__all__"  就表示 对表中所有字段进行，操作
        # 直接指定，数据库中的 Role 角色表。  只对他的title 字段， 进行操作。
        widgets = {"title": forms.TextInput(attrs={"class": "form-control"})}
        # 为 input 框， 添加样式， 利用widgets小工具