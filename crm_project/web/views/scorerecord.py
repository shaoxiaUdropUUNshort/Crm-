#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/24
from stark.servers.start_v1 import StartHandler, StarkModelForm
from django.urls import re_path
from web import models
from .base import PermissionHandler


class ScoreRecordModelForm(StarkModelForm):
    class Meta:
        model = models.ScoreRecord
        fields = ["content", "score"]


class ScoreRecordHandler(PermissionHandler, StartHandler):
    list_display = ["student", "content", "score", "user"]

    def get_list_display(self, request, *args, **kwargs):
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    def get_queryset(self, request, *args, **kwargs):
        student_id = kwargs.get("student_id")
        return self.model_class.objects.filter(student_id=student_id)

    def get_urls(self):
        partterns = [
            re_path(r"list/(?P<student_id>\d+)/$", self.wrapper(self.check_list_view), name=self.get_list_url_name),
            re_path(r"add/(?P<student_id>\d+)/$", self.wrapper(self.add_view), name=self.get_add_url_name)
        ]
        return partterns

    model_form_class = ScoreRecordModelForm

    def save(self, request, form, is_update, *args, **kwargs):
        current_user_id = request.session["user_info"]["id"]
        current_student_id = kwargs.get("student_id")
        models.Student.objects.filter()
        form.instance.student_id = current_student_id
        form.instance.user_id = current_user_id
        form.save()
        # 通过form 也可以获取到。被关联表的数据. 原分值
        # origin_score = form.instance.student.score
        score = form.instance.score
        if score > 0:
            form.instance.student.score += abs(score)
        else:
            form.instance.student.score -= abs(score)
        form.instance.student.save()
