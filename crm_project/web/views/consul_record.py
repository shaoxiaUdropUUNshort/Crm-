#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/22
from stark.servers.start_v1 import StartHandler, StarkModelForm, get_choice_text, get_datetime_text
from django.urls import re_path
from stark.forms.plug_in import DateTimePickerInput
from django.shortcuts import render, redirect, HttpResponse
from django.utils.safestring import mark_safe
from web import models
from .base import PermissionHandler


class ConsultRecordModelForm(PermissionHandler,StartHandler):
    class Meta:
        model = models.ConsultRecord
        fields = ["note"]


class ConsultRecordHandler(StartHandler):
    list_display = ["note", "consultant", get_datetime_text("跟进时间", "date")]

    check_list_template = "consult_record_detail.html"
    model_form_class = ConsultRecordModelForm

    def save(self, request, form, is_update, *args, **kwargs):
        current_consultant_id = request.session.get("user_info").get("id")
        current_customer_id = kwargs.get('customer_id')
        object_exists = models.Customer.objects.filter(id=current_customer_id,
                                                       consultant_id=current_consultant_id).exists()
        if not object_exists:
            return HttpResponse("非法操作")
        if not is_update:
            form.instance.consultant_id = current_consultant_id
            form.instance.customer_id = current_customer_id
        form.save()

    def display_edit_and_display_del(self, obj=None, is_header=None, *args, **kwargs):
        customer_id = kwargs.get("customer_id")
        if is_header:
            return "操作"
        return mark_safe(
            "<a href='%s'><i class='fa fa-edit' aria-hidden='true' style='position:relative;top:1px;'></i></a> | "
            "<a href='%s' style='color:#f44336'><i class='fa fa-trash-o' aria-hidden='true'></i></a>"
            % (self.memory_url(get_url_name=self.get_edit_url_name, pk=obj.pk, customer_id=customer_id),
               self.memory_url(get_url_name=self.get_del_url_name, pk=obj.pk, customer_id=customer_id)))

    # def get_list_display(self):
    #     '''get_list_display 这个方法,是优先查找自己类的.所以我在这里重写，并且编辑删除按钮的 href 使用的是自己类中的，方法'''
    #     '''但是这种写法， 很low。 我下面写了，高级的用法。 并且在父类中使用改用法。'''
    #     value = []
    #     if self.list_display:
    #         value.extend(self.list_display)
    #         value.append(ConsultRecordHandler.display_edit_and_display_del)
    #         # value.append(type(self).display_edit_and_display_del)  # 这种写法就是优先去 自己的类中找。
    #         # 这传代码，没有用。 留在这里做个记录。
    #     return value

    def get_urls(self):
        partterns = [
            re_path(r"list/(?P<customer_id>\d+)/$", self.wrapper(self.check_list_view), name=self.get_list_url_name),
            re_path(r"add/(?P<customer_id>\d+)/$", self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r"change/(?P<customer_id>\d+)/(?P<pk>\d+)/$", self.wrapper(self.change_view),
                    name=self.get_edit_url_name),
            re_path(r"del/(?P<customer_id>\d+)/(?P<pk>\d+)/$", self.wrapper(self.delete_view),
                    name=self.get_del_url_name),
        ]
        return partterns

    def get_queryset(self, request, *args, **kwargs):
        current_customer_id = kwargs.get("customer_id")
        current_user_id = request.session.get("user_info").get('id')
        return self.model_class.objects.filter(customer_id=current_customer_id, customer__consultant_id=current_user_id)

    def get_change_object(self, request, pk, *args, **kwargs):
        current_customer_id = kwargs.get("customer_id")
        current_user_id = request.session.get("user_info").get('id')
        return models.ConsultRecord.objects.filter(pk=pk, customer_id=current_customer_id,
                                                   consultant_id=current_user_id).first()

    def get_delete_object(self, request, pk, *args, **kwargs):
        '''扩展，过滤条件'''
        current_customer_id = kwargs.get("customer_id")
        current_user_id = request.session.get("user_info").get('id')
        record_queryset = models.ConsultRecord.objects.filter(pk=pk, customer_id=current_customer_id,
                                                              consultant_id=current_user_id)
        if not record_queryset:
            return HttpResponse("要删除的记录，不存在")
        record_queryset.delete()
