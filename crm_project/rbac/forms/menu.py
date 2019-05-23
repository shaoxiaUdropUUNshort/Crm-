#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/15

from django import forms
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from rbac import models
from rbac.forms.BASE import BootstrapModelForm

# mark_safe 告诉django这个是安全的，渲染页面时， 不要转换成特殊符号。

ICON_LIST = [
    ['fa-hand-scissors-o', '<i aria-hidden="true" class="fa fa-hand-scissors-o"></i>'],
    ['fa-hand-spock-o', '<i aria-hidden="true" class="fa fa-hand-spock-o"></i>'],
    ['fa-hand-stop-o', '<i aria-hidden="true" class="fa fa-hand-stop-o"></i>'],
    ['fa-handshake-o', '<i aria-hidden="true" class="fa fa-handshake-o"></i>'],
    ['fa-hard-of-hearing', '<i aria-hidden="true" class="fa fa-hard-of-hearing"></i>'],
    ['fa-hashtag', '<i aria-hidden="true" class="fa fa-hashtag"></i>'],
    ['fa-hdd-o', '<i aria-hidden="true" class="fa fa-hdd-o"></i>'],
    ['fa-headphones', '<i aria-hidden="true" class="fa fa-headphones"></i>'],
    ['fa-heart', '<i aria-hidden="true" class="fa fa-heart"></i>'],
    ['fa-heart-o', '<i aria-hidden="true" class="fa fa-heart-o"></i>'],
    ['fa-heartbeat', '<i aria-hidden="true" class="fa fa-heartbeat"></i>'],
    ['fa-history', '<i aria-hidden="true" class="fa fa-history"></i>'],
    ['fa-home', '<i aria-hidden="true" class="fa fa-home"></i>'],
    ['fa-hotel', '<i aria-hidden="true" class="fa fa-hotel"></i>'],
    ['fa-hourglass', '<i aria-hidden="true" class="fa fa-hourglass"></i>'],
    ['fa-hourglass-1', '<i aria-hidden="true" class="fa fa-hourglass-1"></i>'],
    ['fa-hourglass-2', '<i aria-hidden="true" class="fa fa-hourglass-2"></i>'],
    ['fa-hourglass-3', '<i aria-hidden="true" class="fa fa-hourglass-3"></i>'],
    ['fa-hourglass-end', '<i aria-hidden="true" class="fa fa-hourglass-end"></i>'],
    ['fa-hourglass-half', '<i aria-hidden="true" class="fa fa-hourglass-half"></i>'],
    ['fa-hourglass-o', '<i aria-hidden="true" class="fa fa-hourglass-o"></i>'],
    ['fa-hourglass-start', '<i aria-hidden="true" class="fa fa-hourglass-start"></i>'],
    ['fa-i-cursor', '<i aria-hidden="true" class="fa fa-i-cursor"></i>'],
    ['fa-id-badge', '<i aria-hidden="true" class="fa fa-id-badge"></i>'],
    ['fa-id-card', '<i aria-hidden="true" class="fa fa-id-card"></i>'],
    ['fa-id-card-o', '<i aria-hidden="true" class="fa fa-id-card-o"></i>'],
    ['fa-image', '<i aria-hidden="true" class="fa fa-image"></i>'],
    ['fa-mail-reply-all', '<i aria-hidden="true" class="fa fa-mail-reply-all"></i>'],
    ['fa-reply', '<i aria-hidden="true" class="fa fa-reply"></i>'],
    ['fa-reply-all', '<i aria-hidden="true" class="fa fa-reply-all"></i>'],
    ['fa-retweet', '<i aria-hidden="true" class="fa fa-retweet"></i>'],
    ['fa-wrench', '<i aria-hidden="true" class="fa fa-wrench"></i>']]

for item in ICON_LIST:
    item[1] = mark_safe(item[1])


class MenuForm(forms.ModelForm):
    '''菜单form'''

    class Meta:
        model = models.Menu
        fields = ["title", "icon"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "icon": forms.RadioSelect(
                choices=ICON_LIST,
                attrs={'class': 'clearfix'}
            )
        }


class SecondMenuForm(BootstrapModelForm):
    '''菜单form'''

    class Meta:
        model = models.Permission
        exclude = ["pid"]  # 取消掉pid字段，因为pid属于是，不能作为二级菜单的存在， 只有menu字段有值的才是二级菜单
    # def __init__(self, *args, **kwargs):
    #     super(SecondMenuForm, self).__init__(*args, **kwargs)
    #     # 循环父类中生成的所有的字段，为每一个字段添加样式, 一次性为所有字典添加样式
    #     for name, field in self.fields.items():
    #         field.widget.attrs["class"] = "form-control"


class PermissionForm(BootstrapModelForm):
    class Meta:
        model = models.Permission
        fields = ["title", "name", "url"]


class MultiAddPermissionForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    url = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    menu_id = forms.ChoiceField(  # ChoiceField 和 choices 就表示数据源
        choices=[(None, "---------")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )
    pid_id = forms.ChoiceField(
        choices=[(None, "---------")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["menu_id"].choices += models.Menu.objects.values_list("mid", "title")
        self.fields["pid_id"].choices += models.Permission.objects.filter(pid__isnull=True).exclude(
            menu__isnull=True).values_list("id", "title")


class MultiEditPermissionForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    url = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    menu_id = forms.ChoiceField(  # ChoiceField 和 choices 就表示数据源
        choices=[(None, "---------")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )
    pid_id = forms.ChoiceField(
        choices=[(None, "---------")],
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["menu_id"].choices += models.Menu.objects.values_list("mid", "title")
        self.fields["pid_id"].choices += models.Permission.objects.filter(pid__isnull=True).exclude(
            menu__isnull=True).values_list("id", "title")
