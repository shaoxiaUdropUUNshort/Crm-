#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/21
from stark.servers.start_v1 import site
from web import models
from web.views.school import SchoolHandler
from web.views.department import DepartmentHandler
from web.views.userinfo import UserInfoHandler
from web.views.course import CourseHandler
from web.views.classlist import ClassListHandler
from web.views.public_customer import PublicCustomerHandler
from web.views.private_customer import PrivateCustomerHandler
from web.views.consul_record import ConsultRecordHandler
from web.views.payment_record import PaymentRecordHandler
from web.views.check_payment_record import CheckPaymentRecordHandler
from web.views.student import StudentHandler
from web.views.scorerecord import ScoreRecordHandler
from web.views.courserecord import CourseRecordHandler


site.register(models.School, SchoolHandler)
site.register(models.Department, DepartmentHandler)
site.register(models.UserInfo, UserInfoHandler)
site.register(models.Course, CourseHandler)
site.register(models.ClassList, ClassListHandler)
site.register(models.Customer, PublicCustomerHandler, "pub")
site.register(models.Customer, PrivateCustomerHandler, "pri")
site.register(models.ConsultRecord, ConsultRecordHandler,)
site.register(models.PaymentRecord, PaymentRecordHandler,)
site.register(models.PaymentRecord, CheckPaymentRecordHandler, "check")
site.register(models.Student, StudentHandler)
site.register(models.ScoreRecord, ScoreRecordHandler)
site.register(models.CourseRecord, CourseRecordHandler)

