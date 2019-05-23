#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/22
from web import models
from django.utils.safestring import mark_safe
from django.urls import re_path
from django.shortcuts import render, redirect, HttpResponse
from stark.servers.start_v1 import StartHandler, get_choice_text, get_manytomany_text, StarkModelForm
from django.db import transaction
from .base import PermissionHandler


class PublicCustomerModelForm(StarkModelForm):
    class Meta:
        model = models.Customer
        exclude = ["consultant"]


class PublicCustomerHandler(PermissionHandler,StartHandler):

    def display_record(self, obj=None, is_header=None):
        if is_header:
            return "跟进记录"
        record_url = self.memory_url(get_url_name=self.get_url_name("record_view"), pk=obj.pk)
        return mark_safe("<a href='%s'>查看跟进</a>" % record_url)

    def record_detail_view(self, request, pk):
        consultant_record = models.ConsultRecord.objects.filter(customer_id=pk)
        return render(request, "record_detail.html", {"record_list": consultant_record})

    def extra_url(self):
        '''在现有的url基础上 再增加一个url。 但是视图函数需要自己写了'''
        partterns = [
            re_path(r"record/(?P<pk>\d+)/$", self.wrapper(self.record_detail_view),
                    name=self.get_url_name("record_view")),
        ]
        return partterns

    list_display = [StartHandler.display_checkbox, "name", "qq", get_choice_text("状态", "status"),
                    get_choice_text("性别", "gender"), "date",
                    get_manytomany_text("咨询课程", "course"), get_choice_text("来源", "source"), display_record]

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)

    model_form_class = PublicCustomerModelForm

    def action_multi_apply(self, request, *args, **kwargs):
        '''
        批量申请客户到，私户. 将consultant_id 更新为， 当前的登陆的用户userinfo。
        使用批量功能时 StartHandler.display_checkbox 需要添加到  list_display中。
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        current_user_id = request.session.get("user_info").get('id')
        pk_list = request.POST.getlist("pk")

        private_customer_count = models.Customer.objects.filter(consultant_id=current_user_id, status=2).count()
        # 客户个数限制。
        if (private_customer_count + len(pk_list)) > models.Customer.MAX_PRIVATE_CUSTOMER_COUNT:
            respons = "做人不能太贪心,私户中已有%s个客户,最多只能申请%s个客户" % (
                private_customer_count, models.Customer.MAX_PRIVATE_CUSTOMER_COUNT - private_customer_count)
            return HttpResponse(respons)

        #  需要对表加锁。 防止一个同时申请操作的，极限情况。 而发生申请数据的紊乱。 在Django加锁，需要先引入事物

        flag = False
        with transaction.atomic():  # 开始事物
            # 在数据库中加锁。 select * from customer where id in [11,22] for update
            origin_queryset = models.Customer.objects.filter(id__in=pk_list, status=2,
                                                             consultant__isnull=True).select_for_update()
            # origin_queryset 从数据库取到的，未更新的 数据。 当这个事物的上下文，走出去之后。 下一个申请才会进来
            if len(origin_queryset) == len(pk_list):
                models.Customer.objects.filter(id__in=pk_list, status=2, consultant__isnull=True).update(
                    consultant_id=current_user_id)
                flag = True

        if not flag:
            return HttpResponse("手速太慢了，选中的客户。已被其他人申请走。 请重新选择")

    action_multi_apply.text = "批量申请到私户"

    action_list = [action_multi_apply]

