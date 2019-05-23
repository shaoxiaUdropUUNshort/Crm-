#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/24
from stark.servers.start_v1 import StartHandler, StarkModelForm, get_datetime_text
from django.urls import re_path, reverse
from django.utils.safestring import mark_safe
from django.forms.models import modelformset_factory
from django.shortcuts import HttpResponse, render, redirect
from web import models
from .base import PermissionHandler


class CourseRecordModelForm(PermissionHandler, StarkModelForm):
    class Meta:
        model = models.CourseRecord
        fields = ["day_num", "teacher"]


class StudyRecordModelForm(StarkModelForm):
    class Meta:
        model = models.StudyRecord
        fields = ["record"]


class CourseRecordHandler(StartHandler):
    def display_attendance(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "考勤"
        name = "%s:%s" % (self.site.namespace, self.get_url_name("attendance"))
        return mark_safe("<a target='_black' href='%s'>考勤</a>" % reverse(name, kwargs={"course_record_id": obj.pk}))

    list_display = [StartHandler.display_checkbox, "class_object", "day_num", "teacher",
                    get_datetime_text("上课日期", "date"), display_attendance]

    def display_edit_and_display_del(self, obj=None, is_header=None, *args, **kwargs):
        class_id = kwargs.get("class_id")
        if is_header:
            return "操作"
        return mark_safe(
            "<a href='%s'><i class='fa fa-edit' aria-hidden='true' style='position:relative;top:1px;'></i></a> | "
            "<a href='%s' style='color:#f44336'><i class='fa fa-trash-o' aria-hidden='true'></i></a>"
            % (self.memory_url(get_url_name=self.get_edit_url_name, pk=obj.pk, class_id=class_id),
               self.memory_url(get_url_name=self.get_del_url_name, pk=obj.pk, class_id=class_id)))

    def get_urls(self):
        partterns = [
            re_path(r"list/(?P<class_id>\d+)/$", self.wrapper(self.check_list_view), name=self.get_list_url_name),
            re_path(r"add/(?P<class_id>\d+)/$", self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r"change/(?P<class_id>\d+)/(?P<pk>\d+)/$", self.wrapper(self.change_view),
                    name=self.get_edit_url_name),
            re_path(r"del/(?P<class_id>\d+)/(?P<pk>\d+)/$", self.wrapper(self.delete_view), name=self.get_del_url_name),
            re_path(r"attendance/(?P<course_record_id>\d+)/$", self.wrapper(self.attendance_view),
                    name=self.get_url_name("attendance"))
        ]
        return partterns

    def get_queryset(self, request, *args, **kwargs):
        class_id = kwargs.get("class_id")
        return self.model_class.objects.filter(class_object_id=class_id)

    model_form_class = CourseRecordModelForm

    def save(self, request, form, is_update, *args, **kwargs):
        class_id = kwargs.get("class_id")
        if not is_update:
            form.instance.class_object_id = class_id
        form.save()

    def action_multi_init(self, request, *args, **kwargs):
        class_id = kwargs.get("class_id")
        course_record_id_list = request.POST.getlist("pk")
        class_obj = models.ClassList.objects.filter(id=class_id).first()
        if not class_obj:
            return HttpResponse("没有找到班级")
        student_object_list = class_obj.student_set.all()
        for course_record_id in course_record_id_list:
            # 判断上课记录，是否合法。 是否有这个上课记录，班级记录是否正确。 如果为空的话，说明 课程记录的id 和 班级id 没有对上.
            # 就说明，这条记录是，不合法的
            courserecord_obj = models.CourseRecord.objects.filter(id=course_record_id, class_object_id=class_id).first()
            if not courserecord_obj:
                continue
            # 判断此上课记录的，学生考勤记录是否已经存在。 如果已存在就跳过。
            study_record_exists = models.StudyRecord.objects.filter(course_record=courserecord_obj).first()
            if study_record_exists:
                continue
            # 为每个学员，在这一天创建上课纪律
            # for stu in student_object_list:
            #     models.StudyRecord.objects.create(course_record_id=course_record_id, student_id=stu.id)
            study_record_object_list = [
                models.StudyRecord(course_record_id=course_record_id, student_id=stu.id) for stu in student_object_list
            ]  # 此种方式时创建了，很多的上课纪律的对象。
            models.StudyRecord.objects.bulk_create(study_record_object_list, batch_size=50)
            # 然后再进行保存. batch_size 指定每次保存多少条。

    action_multi_init.text = "批量初始化考勤"

    action_list = [action_multi_init]

    def attendance_view(self, request, course_record_id, *args, **kwargs):
        '''考勤的批量操作'''
        study_record_list = models.StudyRecord.objects.filter(course_record_id=course_record_id)
        study_model_formset = modelformset_factory(models.StudyRecord, form=StudyRecordModelForm, extra=0)
        if request.method == "POST":
            formset = study_model_formset(queryset=study_record_list, data=request.POST)
            if formset.is_valid():
                formset.save()
            return render(request, "attendance.html", {"formset": formset})

        formset = study_model_formset(queryset=study_record_list)
        return render(request, "attendance.html", {"formset": formset})

    # instence
    # form.instence  formset将为得到的queryset中的每个对象，生成一个form对象。 form中的instence代指的就是，从数据库中取出的那一行数据
    # 所以，这个instence中。才有每行数据，他自己的字段。就可以使用 点语法。赋值或者获取值等
    #  {{ formset.management_form }}  使用formset时， 这一句，模板中必须加上
