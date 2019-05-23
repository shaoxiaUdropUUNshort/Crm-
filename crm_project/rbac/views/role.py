#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/14


'''角色管理'''
from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from django.urls import reverse
from rbac import models
from rbac.forms.role import RolemodelForm


def role_list(request):
    '''
    角色列表的功能
    :param request:
    :return:
    '''
    role_queryset = models.Role.objects.all()
    return render(request, "rbac/role_list.html", locals())


def role_add(request):
    '''
    添加角色的功能
    :param request:
    :return:
    '''
    forms = RolemodelForm()
    if request.method == "POST":
        forms = RolemodelForm(request.POST)
        if forms.is_valid():  # 验证成功
            forms.save()  # 进行保存
            return redirect(reverse("rbac:role_list"))  # 跳转到role_list
        else:
            return render(request, "rbac/change.html", {"forms": forms})  # 验证失败，返回带有错误信息的页面
    return render(request, "rbac/change.html", {"forms": forms})


def role_edit(request, pk):
    '''
    编辑角色
    :param request:
    :param pk:   要修改的角色id
    :return:
    '''
    role_obj = models.Role.objects.filter(pk=pk).first()
    if not role_obj:
        return HttpResponse("角色不存在")

    if request.method == "POST":
        forms = RolemodelForm(instance=role_obj, data=request.POST)
        if forms.is_valid():
            forms.save()
            return redirect(reverse("rbac:role_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = RolemodelForm(instance=role_obj)  # 将查询出来的对象交给form组件， 进行渲染。
    # instance 就是接收一个 从数据库中，取出的模型表的这样一个数据。

    # 这里为什么返回的是，添加的页面？ 因为添加个编辑一模一样， 只是input框中有数据而已。 而我现在的forms中已经有了数据
    return render(request, "rbac/change.html", {"forms": forms})


def role_del(request, pk):
    '''
    删除操作， 需要给与用户提示。
    :param reuqest:
    :param pk:  要删除的角色id
    :return:
    '''
    origin_url = reverse("rbac:role_list")
    role_queryset = models.Role.objects.filter(pk=pk)
    if not role_queryset:
        return HttpResponse("角色不存在")
    if request.method == "POST":
        role_queryset.delete()
        return redirect(origin_url)
    return render(request, "rbac/delete.html", {"cancel": origin_url})
