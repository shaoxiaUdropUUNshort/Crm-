#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/22
from stark.servers.start_v1 import StartHandler, StarkModelForm, get_manytomany_text, get_choice_text, get_datetime_text
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.utils.safestring import mark_safe
from web import models
from .base import PermissionHandler


class PrivateCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ["consultant"]


class PrivateCustomerHandler(PermissionHandler, StartHandler):

    def display_record(self, obj=None, is_header=None):

        if is_header:
            return "跟进"
        record_url = reverse("stark:web_consultrecord_list", kwargs={"customer_id": obj.pk})
        return mark_safe("<a target='_black' href='%s'>跟进</a>" % record_url)

    def display_pay_record(self, obj=None, is_header=None):
        if is_header:
            return "缴费"
        record_url = reverse("stark:web_paymentrecord_list", kwargs={"customer_id": obj.pk})
        return mark_safe("<a target='_black' href='%s'>缴费</a>" % record_url)

    list_display = [StartHandler.display_checkbox, "name", "qq", get_choice_text("状态", "status"),
                    get_choice_text("性别", "gender"), "date", get_manytomany_text("咨询课程", "course"),
                    get_choice_text("来源", "source"), display_record, display_pay_record]

    def get_queryset(self, request, *args, **kwargs):
        '''重写基类功能， 过滤出。当前用户的所有的， 用户信息！'''
        current_user_id = request.session["user_info"]["id"]
        return self.model_class.objects.filter(consultant_id=current_user_id)

    def save(self, request, form, is_update, *args, **kwargs):
        if not is_update:
            current_user_id = request.session["user_info"]["id"]
            # 使用instance 为剔除出去的consultant字段。添加一个值用于保存。 私户中的值为，当前访问的userinfo中的用户。
            form.instance.consultant_id = current_user_id
            form.save()

    model_form_class = PrivateCustomerModelForm

    # 私户剔除到公户。 使用action
    def action_multi_remove(self, request, *args, **kwargs):
        '''
        批量从私户中将客户移除，客户将移动到公户中. 将consultant_id 更新为Null
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        current_user_id = request.session.get("user_info").get('id')
        pk_list = request.POST.getlist("pk")
        # 限制上，属于当前用户(也就是课程顾问是当前用户的那些数据) 防止技术人员搞破坏
        self.model_class.objects.filter(id__in=pk_list, consultant_id=current_user_id).update(consultant=None)

    action_multi_remove.text = "移除到公户"

    action_list = [action_multi_remove]

    # 跟进记录的管理！ 这也就是没有单独为，记录表创建 url 的原因。 因为这些操作。 需要用户在他自己的客户展示页面做这些操作。
    # 公户中，只有查看，跟进记录的功能。 私户就需要 增删改查全都有。(并且还有可能 删和改的权限不能全部开放的问题)
