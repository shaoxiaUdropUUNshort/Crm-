#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/24
from stark.servers.start_v1 import StartHandler, get_choice_text, get_manytomany_text, StarkModelForm, Option
from django.urls import re_path, reverse
from django.utils.safestring import mark_safe
from web import models
from .base import PermissionHandler


class StudentModelForm(PermissionHandler, StarkModelForm):
    class Meta:
        model = models.Student
        fields = ["qq", "mobile", "emergency_contract", "memo"]


class StudentHandler(StartHandler):
    has_add_btn = False
    def display_score(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "积分记录"
        record_url = reverse("stark:web_scorerecord_list", kwargs={"student_id": obj.pk})
        return mark_safe("<a target='_black' href='%s'>%s</a>" % (record_url, obj.score))

    list_display = ["customer", "qq", "mobile", "emergency_contract", get_manytomany_text("以报班级", "class_list"),
                    get_choice_text("状态", "student_status"), display_score]

    model_form_class = StudentModelForm

    def get_list_display(self, request, *args, **kwargs):
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_edit)
        return value

    def get_urls(self):
        partterns = [
            re_path(r"list/$", self.wrapper(self.check_list_view), name=self.get_list_url_name),
            re_path(r"change/(?P<pk>\d+)/$", self.wrapper(self.change_view), name=self.get_edit_url_name),
        ]
        return partterns

    search_list = ["customer__name", "qq", "mobile"]

    search_group = [
        Option("class_list", is_multi=True, text_func=lambda x: "%s-%s" % (x.school.title, str(x)))
    ]
