#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/22
from stark.servers.start_v1 import StartHandler, get_datetime_text, get_manytomany_text, StarkModelForm, Option
from django.utils.safestring import mark_safe
from django.urls import reverse
from web import models
from stark.forms.plug_in import DateTimePickerInput
from .base import PermissionHandler


class DateTimeModelForm(PermissionHandler,StartHandler):
    class Meta:
        model = models.ClassList
        fields = "__all__"
        widgets = {
            "start_date": DateTimePickerInput,
            "graduate_date": DateTimePickerInput,
        }


class ClassListHandler(StartHandler):
    def display_course_record(self, obj=None, is_header=None):

        if is_header:
            return "上课记录"
        record_url = reverse("stark:web_courserecord_list", kwargs={"class_id": obj.pk})
        return mark_safe("<a target='_black' href='%s'>记录</a>" % record_url)

    def display_course(self, obj=None, is_header=None):
        if is_header:
            return "班级"
        return "%s (%s)期" % (obj.course.name, obj.semester)

    list_display = ['school',
                    display_course,
                    get_datetime_text("开班日期", 'start_date'),
                    get_datetime_text("结课日期", 'graduate_date'),
                    "class_teacher",
                    get_manytomany_text("任课老师", 'tech_teachers'),
                    display_course_record,
                    'memo']

    model_form_class = DateTimeModelForm

    search_group = [
        Option('school'),
        Option('course'),
        Option('tech_teachers'),
    ]

    search_list = ["semester__contains"]
