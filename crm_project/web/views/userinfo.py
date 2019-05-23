#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/22
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.urls import re_path
from django.shortcuts import render, redirect, HttpResponse
from stark.servers.start_v1 import StartHandler, get_choice_text, StarkModelForm, StarkForm, get_manytomany_text
from stark.servers.start_v1 import Option
from web import models
from web.utils import pwdmd5
from .base import PermissionHandler


class UserInfoADDModelForm(StarkModelForm):
    '''定制用户添加 form。 增加一个 确认密码字段， 并且需要增加验证'''
    confirm_password = forms.CharField(label="确认密码", widget=forms.PasswordInput)

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "confirm_password", "nickname", "gender", "telephone", "email", "depart", "roles"]

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data["confirm_password"]
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("两次密码输入不一致")
            return confirm_password  # 验证完成一定要返回，才能添加到 cleaned_data 字典中. 其他地方才能通过cleaned_data获取到

    def clean(self):
        '''对密码进行加密， 可以在clean 里面来做。'''
        password = self.cleaned_data["password"]
        self.cleaned_data["password"] = pwdmd5.creatr_md5(password)
        return self.cleaned_data


class UserInfoEditModelForm(StarkModelForm):
    '''定制用户编辑 form。不显示密码字段。'''

    class Meta:
        model = models.UserInfo
        fields = ["name", "nickname", "gender", "telephone", "email", "depart", "roles"]


class ResetPassword(StarkForm):
    password = forms.CharField(label="密码", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="确认密码", widget=forms.PasswordInput)

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("两次密码输入不一致")
            return confirm_password

    def clean(self):
        '''对密码进行加密， 可以在clean 里面来做。'''
        password = self.cleaned_data["password"]
        self.cleaned_data["password"] = pwdmd5.creatr_md5(password)
        return self.cleaned_data


class UserInfoHandler(PermissionHandler, StartHandler):

    def display_reset_pwd(self, obj=None, is_header=None):
        if is_header:
            return "重置密码"
        rest_url = self.memory_url(get_url_name=self.get_url_name("reset_pwd"), pk=obj.pk)
        return mark_safe("<a href='%s'>重置密码</a>" % rest_url)

    list_display = ["name", "nickname", "age", get_choice_text("性别", "gender"), "telephone", "email", "depart",
                    get_manytomany_text("拥有的角色", "roles"), display_reset_pwd]

    def reset_password(self, request, pk):
        '''重置密码的视图函数'''
        userinfo_obj = models.UserInfo.objects.filter(pk=pk).first()
        if not userinfo_obj:
            return HttpResponse("用户不存在,无法重置密码")
        if request.method == "POST":
            form = ResetPassword(request.POST)
            if form.is_valid():
                userinfo_obj.password = form.cleaned_data["password"]
                userinfo_obj.save()
                return redirect(self.memory_reverse(get_url_name=self.get_list_url_name))
            return render(request, "stark/change.html", {"form": form})
        form = ResetPassword()
        return render(request, "stark/change.html", {"form": form})

    def extra_url(self):
        '''在现有的url基础上 再增加一个url。 但是视图函数需要自己写了'''
        partterns = [
            re_path(r"reset/pwd/(?P<pk>\d+)/$", self.wrapper(self.reset_password), name=self.get_url_name("reset_pwd")),
        ]
        return partterns

    def get_model_form_class(self, is_add, request, pk, *args, **kwargs):
        if is_add:
            return UserInfoADDModelForm
        return UserInfoEditModelForm

    search_list = ["nickname__contains", "name__contains"]  # 关键字搜索， 自行根据ORM语法，添加，对应字段的规则
    search_group = [
        Option(field="gender"),
        Option(field="depart", is_multi=True)
    ]  # 组合搜索的应用。 可设置多选，单选等等。