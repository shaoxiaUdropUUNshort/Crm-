#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/22
from django import forms


class DateTimePickerInput(forms.TextInput):
    '''替换掉TextInput源码中，选择的html文件。而使用我自己定义的插件'''
    template_name = 'stark/forms/widgets/datetime_picker.html'
