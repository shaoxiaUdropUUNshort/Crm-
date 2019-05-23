#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/15


from django import forms


class BootstrapModelForm(forms.ModelForm):
    '''
    因为，太多的地方需要使用， __init__ 初始化方式。来对每个标签添加 class="form-control" 所以搞个基类让
    要进行， 这部操作的 类去继承，
    '''
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"