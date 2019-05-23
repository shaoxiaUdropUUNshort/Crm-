#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/24
from stark.servers.start_v1 import StartHandler, get_choice_text, get_datetime_text
from django.urls import re_path
from django.db.models import Q
from .base import PermissionHandler


class CheckPaymentRecordHandler(PermissionHandler, StartHandler):
    list_display = [StartHandler.display_checkbox, "customer", "consultant", get_choice_text("缴费类型", "pay_type"),
                    "paid_fee", "class_list",
                    get_datetime_text("申请日期", "apply_date"), get_choice_text("状态", "confirm_status")]

    has_add_btn = False

    def get_list_display(self, request, *args, **kwargs):
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    def get_urls(self):
        partterns = [
            re_path(r"list/$", self.wrapper(self.check_list_view), name=self.get_list_url_name),
        ]
        return partterns

    def action_multi_confirm(self, request, *args, **kwargs):
        '''
        批量确认
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        pk_list = request.POST.getlist("pk")
        # 缴费记录表
        # 客户表
        # 学生表
        # 三张表的，状态应该。 同时改变
        for pk in pk_list:
            payment_obj = self.model_class.objects.filter(id=pk, confirm_status=1).first()
            if not payment_obj:
                continue
            # 自己表的状态改为2
            payment_obj.confirm_status = 2
            payment_obj.save()
            # 通过customer字段。找到 客户表中的 status。 改为1
            payment_obj.customer.status = 1
            payment_obj.customer.save()
            # 通过customer字段。找到客户表，再通过反向查找找到 student表。 student表的 student_status 改为2
            payment_obj.customer.student.student_status = 2
            payment_obj.customer.student.save()

    action_multi_confirm.text = "批量确认"

    def action_multi_cancel(self, request, *args, **kwargs):
        self.model_class.objects.filter(id__in=request.POST.getlist("pk"), confirm_status=1).update(confirm_status=3)

    action_multi_cancel.text = "批量驳回"

    # def action_multi_dropout(self, request, *args, **kwargs):
    #     pk_list = request.POST.getlist("pk")
    #     for pk in pk_list:
    #         # Q(id=pk) | ~Q(confirm_status=1)
    #         payment_obj = self.model_class.objects.filter(Q(id=pk), Q(confirm_status=2)).first()
    #         if not payment_obj:
    #             continue
    #         payment_obj.confirm_status = 4
    #         payment_obj.save()
    #         payment_obj.customer.status = 2
    #         payment_obj.customer.save()
    #         payment_obj.customer.student.student_status = 4
    #         payment_obj.customer.student.save()
    #     action_multi_dropout
    # action_multi_dropout.text = "批量退学"

    ordered_list = ["-id", "confirm_status"]

    action_list = [action_multi_confirm, action_multi_cancel, StartHandler.action_multi_delete]
