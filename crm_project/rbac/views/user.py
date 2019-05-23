#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/14


'''角色管理'''
from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from django.urls import reverse
from rbac import models
from rbac.forms.user import UserInfoModelForm, UpdateUserInfoModelForm, ResetPasswordUserInfoModelForm


def user_list(request):
    '''
    角色列表的功能
    :param request:
    :return:
    '''
    user_queryset = models.UserInfo.objects.all()
    return render(request, "rbac/user_list.html", locals())


def user_add(request):
    '''
    添加角色的功能
    :param request:
    :return:
    '''
    forms = UserInfoModelForm()
    if request.method == "POST":
        forms = UserInfoModelForm(request.POST)
        if forms.is_valid():  # 验证成功
            forms.save()  # 进行保存
            return redirect(reverse("rbac:user_list"))  # 跳转到role_list
        else:
            return render(request, "rbac/change.html", {"forms": forms})  # 验证失败，返回带有错误信息的页面
    return render(request, "rbac/change.html", {"forms": forms})


def user_edit(request, pk):
    '''
    编辑角色
    :param request:
    :param pk:   要修改的角色id
    :return:
    '''
    user_obj = models.UserInfo.objects.filter(pk=pk).first()
    if not user_obj:
        return HttpResponse("用户不存在")

    if request.method == "POST":
        forms = UpdateUserInfoModelForm(instance=user_obj, data=request.POST)
        if forms.is_valid():
            forms.save()
            return redirect(reverse("rbac:user_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = UpdateUserInfoModelForm(instance=user_obj)  # 将查询出来的对象交给form组件， 进行渲染。
    # instance 就是接收一个 从数据库中，取出的模型表的这样一个数据。

    # 这里为什么返回的是，添加的页面？ 因为添加个编辑一模一样， 只是input框中有数据而已。 而我现在的forms中已经有了数据
    return render(request, "rbac/change.html", {"forms": forms})


def user_del(request, pk):
    '''
    删除操作， 需要给与用户提示。
    :param reuqest:
    :param pk:  要删除的角色id
    :return:
    '''
    origin_url = reverse("rbac:user_list")
    role_queryset = models.UserInfo.objects.filter(pk=pk)
    if not role_queryset:
        return HttpResponse("角色不存在")
    if request.method == "POST":
        role_queryset.delete()
        return redirect(origin_url)
    return render(request, "rbac/delete.html", {"cancel": origin_url})


def reset_pwd(request, pk):
    '''
    重置密码
    :param request:
    :param pk:
    :return:
    '''
    user_obj = models.UserInfo.objects.filter(pk=pk).first()
    if not user_obj:
        return HttpResponse("用户不存在")

    if request.method == "POST":
        forms = ResetPasswordUserInfoModelForm(instance=user_obj, data=request.POST)
        if forms.is_valid():
            forms.save()
            return redirect(reverse("rbac:user_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = ResetPasswordUserInfoModelForm()
    return render(request, "rbac/change.html", {"forms": forms})
