#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/24
from stark.servers.start_v1 import StartHandler, get_choice_text, StarkModelForm
from django.urls import re_path, reverse
from django.shortcuts import HttpResponse
from django import forms
from web import models
from .base import PermissionHandler


class PaymentRecordModelForm(PermissionHandler, StarkModelForm):
    class Meta:
        model = models.PaymentRecord
        fields = ["pay_type", 'paid_fee', 'class_list', 'note']


class StudentPaymentRecordModelForm(StarkModelForm, ):
    qq = forms.CharField(label="QQ号")
    mobile = forms.CharField(label="手机号")
    emergency_contract = forms.CharField(label="紧急联系人")

    class Meta:
        model = models.PaymentRecord
        fields = ["pay_type", "paid_fee", "class_list", "qq", "mobile", "emergency_contract", "note"]


class PaymentRecordHandler(StartHandler):
    list_display = [get_choice_text('费用类型', "pay_type"), "paid_fee", "class_list",
                    get_choice_text("状态", "confirm_status"), "consultant", ]

    def get_list_display(self, request, *args, **kwargs):
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    def get_urls(self):
        partterns = [
            re_path(r"list/(?P<customer_id>\d+)/$", self.wrapper(self.check_list_view), name=self.get_list_url_name),
            re_path(r"add/(?P<customer_id>\d+)/$", self.wrapper(self.add_view), name=self.get_add_url_name),
        ]
        return partterns

    def get_queryset(self, request, *args, **kwargs):
        current_customer_id = kwargs.get("customer_id")
        current_user_id = request.session.get("user_info").get('id')
        return self.model_class.objects.filter(customer_id=current_customer_id, customer__consultant_id=current_user_id)

    def get_model_form_class(self, is_add, request, pk, *args, **kwargs):
        '''如果当前客户，有学生信息。则使用PaymentRecordModelForm'''
        current_customer_id = kwargs.get("customer_id")
        student_exists = models.Student.objects.filter(customer_id=current_customer_id).exists()
        if student_exists:
            return PaymentRecordModelForm
        return StudentPaymentRecordModelForm

    def save(self, request, form, is_update, *args, **kwargs):
        current_customer_id = kwargs.get("customer_id")
        current_user_id = request.session.get("user_info").get('id')
        object_exists = models.Customer.objects.filter(id=current_customer_id, consultant_id=current_user_id).exists()
        if not object_exists:
            return HttpResponse("非法操作")
        # 创建缴费信息
        form.instance.consultant_id = current_user_id
        form.instance.customer_id = current_customer_id
        form.save()
        # 创建学生信息：
        fetch_student_obj = models.Student.objects.filter(customer_id=current_customer_id).first()
        class_list = form.cleaned_data["class_list"]  # 这里返回的是，班级对象
        if not fetch_student_obj:
            qq = form.cleaned_data["qq"]
            mobile = form.cleaned_data["mobile"]
            emergency_contract = form.cleaned_data["emergency_contract"]
            student_obj = models.Student.objects.create(customer_id=current_customer_id, qq=qq, mobile=mobile,
                                                        emergency_contract=emergency_contract)
            student_obj.class_list.add(class_list.id)  # 多对多添加，班级。(可加可不加)
            # 当班级id 一样的时候。付费记录虽然会一直增加。但不会影响到班级于学生的，关联关系
        else:
            fetch_student_obj.class_list.add(class_list.id)  # 多对多添加，班级。(可加可不加) 对于已经是学生的，添加班级

