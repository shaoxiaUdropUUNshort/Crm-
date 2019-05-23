#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/15

# from django.http import JsonResponse, Http404
# from django.urls import reverse
from django.shortcuts import HttpResponse, render, redirect
from collections import OrderedDict
from rbac import models
from rbac.forms.menu import MenuForm, SecondMenuForm, PermissionForm, MultiAddPermissionForm, MultiEditPermissionForm
from django.forms import formset_factory
from rbac.service.urls import memory_reverse
from rbac.service.routes import get_all_url_dict
from crm_project import settings
# from django.conf import settings  # 不知为什么  无法引入 RBAC_USER_MODEL_CLASS
from django.utils.module_loading import import_string


def menu_list(request):
    '''
    菜单和权限列表
    :param request:
    :return:
    '''
    # menu_id = int(request.GET.get("mid"))  # 前端判断时，需要一个int类型，而不是str类型。
    menu_id = request.GET.get("mid")  # 或者在前端进行转换，将数字转换成，字符串
    second_menu_id = request.GET.get("sid")

    menu_list = models.Menu.objects.all()
    try:
        if menu_id:
            second_menus = models.Permission.objects.filter(menu_id=menu_id)
        else:
            second_menus = []

        if second_menu_id:
            permissions = models.Permission.objects.filter(pid=second_menu_id)
        else:
            permissions = []
        return render(request, "rbac/menu_list.html", locals())
    except ValueError as e:
        return HttpResponse("查找不存在")


def menu_add(request):
    '''
    添加一级菜单
    :param request:
    :return:
    '''
    if request.method == "POST":
        forms = MenuForm(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect(memory_reverse(request, "rbac:menu_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = MenuForm()
    return render(request, "rbac/change.html", {"forms": forms})


def menu_edit(request, pk):
    '''
       编辑角色
       :param request:
       :param pk:   要修改的角色id
       :return:
       '''
    role_obj = models.Menu.objects.filter(pk=pk).first()
    if not role_obj:
        return HttpResponse("菜单不存在")

    if request.method == "POST":
        forms = MenuForm(instance=role_obj, data=request.POST)
        if forms.is_valid():
            forms.save()
            return redirect(memory_reverse(request, "rbac:menu_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = MenuForm(instance=role_obj)
    # instance 就是接收一个 从数据库中，取出的模型表的这样一个数据。
    return render(request, "rbac/change.html", {"forms": forms})


def menu_del(request, pk):
    '''
    删除操作， 需要给与用户提示。
    :param reuqest:
    :param pk:  要删除的角色id
    :return:
    '''
    origin_url = memory_reverse(request, "rbac:menu_list")
    role_queryset = models.Menu.objects.filter(pk=pk)
    if not role_queryset:
        return HttpResponse("菜单不存在")
    if request.method == "POST":
        role_queryset.delete()
        return redirect(origin_url)
    return render(request, "rbac/delete.html", {"cancel": origin_url})


def second_menu_add(request, menu_id):
    '''
    二级菜单添加视图
    :param request:
    :param menu_id:  已经选中的一级菜单的id（用于设置默认值）
    :return:
    '''
    menu_obj = models.Menu.objects.filter(pk=menu_id).first()
    if request.method == "POST":
        forms = SecondMenuForm(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect(memory_reverse(request, "rbac:menu_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = SecondMenuForm(initial={"menu": menu_obj})  # initial 为form中一个字段，添加默认值
    return render(request, "rbac/change.html", {"forms": forms})


def second_menu_edit(request, pk):
    '''

    :param request:
    :param pk: 当前要编辑的二级菜单, 为什么这了不需要menu_id 了呢？ 因为数据库已经做好了关联，所有不需要了
    :return:
    '''
    permission_obj = models.Permission.objects.filter(pk=pk).first()
    if not permission_obj:
        return HttpResponse("菜单不存在")

    if request.method == "POST":
        forms = SecondMenuForm(instance=permission_obj, data=request.POST)
        if forms.is_valid():
            forms.save()
            return redirect(memory_reverse(request, "rbac:menu_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = SecondMenuForm(instance=permission_obj)  # 将查询出来的对象交给form组件， 进行渲染。
    # instance 就是接收一个 从数据库中，取出的模型表的这样一个数据。

    return render(request, "rbac/change.html", {"forms": forms})


def second_menu_del(request, pk):
    '''
    删除操作， 需要给与用户提示。
    :param reuqest:
    :param pk:  要删除的权限id
    :return:
    '''
    origin_url = memory_reverse(request, "rbac:menu_list")
    permission_queryset = models.Permission.objects.filter(pk=pk)
    if not permission_queryset:
        return HttpResponse("菜单不存在")
    if request.method == "POST":
        permission_queryset.delete()
        return redirect(origin_url)
    return render(request, "rbac/delete.html", {"cancel": origin_url})


def permission_add(request, second_menu_id):
    '''
    添加权限
    :param request:
    :param menu_id:  已经选中的二级菜单的id（用于设置默认值）
    :return:
    '''
    if request.method == "POST":
        forms = PermissionForm(request.POST)
        if forms.is_valid():
            # 在添加页面，用户只输入了三个值 title url name 还需要一个 pid的值。 就是传递过来的second_menu_id
            # 并且传递过来的值，可以在数据库中找到对应的 记录，才行。 而且要在forms.save() 保存之前，加入到form中
            second_menu_obj = models.Permission.objects.filter(pk=second_menu_id).first()
            if not second_menu_obj:
                return HttpResponse("二级菜单存在，请重新选择")
            # forms.instance 中包含了用户提交的所有值。 他就是一个Permission对象：
            # instance = models.Permission(title="", name="", url="")  # 接收用户发来的数据
            # instance.pid = second_menu_obj 然后赋值时，就相当于pid = second_menu_obj。 orm操作，外键可以直接指定一个model对象
            # instance.save 然后保存整个内容。 这也是 forms.save 内部做的事情
            forms.instance.pid = second_menu_obj
            forms.save()
            return redirect(memory_reverse(request, "rbac:menu_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = PermissionForm()
    # 为一级菜单menu字段， 添加默认值。
    return render(request, "rbac/change.html", {"forms": forms})


def permission_edit(request, pk):
    '''
    :param request:
    :param pk: 当前要编辑的二级菜单, 为什么这了不需要menu_id 了呢？ 因为数据库已经做好了关联，所有不需要了
    :return:
    '''
    permission_obj = models.Permission.objects.filter(pk=pk).first()
    if not permission_obj:
        return HttpResponse("菜单不存在")

    if request.method == "POST":
        forms = PermissionForm(instance=permission_obj, data=request.POST)
        if forms.is_valid():
            forms.save()
            return redirect(memory_reverse(request, "rbac:menu_list"))
        else:
            return render(request, "rbac/change.html", {"forms": forms})
    forms = PermissionForm(instance=permission_obj)  # 将查询出来的对象交给form组件， 进行渲染。
    return render(request, "rbac/change.html", {"forms": forms})


def permission_del(request, pk):
    '''
    删除操作， 需要给与用户提示。
    :param reuqest:
    :param pk:  要删除的权限id
    :return:
    '''
    origin_url = memory_reverse(request, "rbac:menu_list")
    permission_queryset = models.Permission.objects.filter(pk=pk)
    if not permission_queryset:
        return HttpResponse("菜单不存在")
    if request.method == "POST":
        permission_queryset.delete()
        return redirect(origin_url)
    return render(request, "rbac/delete.html", {"cancel": origin_url})


def multi_permissions(request):
    '''
    批量操作权限
    :param request:
    :return:
    '''

    post_type = request.GET.get("type")
    generate_formset = None
    update_formset = None
    update_formset_class = formset_factory(MultiEditPermissionForm, extra=0)
    generate_formset_class = formset_factory(MultiAddPermissionForm, extra=0)
    if request.method == "POST" and post_type == "generate":  # 批量添加
        formset = generate_formset_class(data=request.POST)
        if formset.is_valid():
            has_error = False
            object_list = []
            post_row_list = formset.cleaned_data
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                if not row_dict:
                    continue
                try:
                    new_object = models.Permission(**row_dict)
                    new_object.validate_unique()
                    object_list.append(new_object)
                except Exception as e:
                    formset.errors[i].update(e)
                    generate_formset = formset
                    has_error = True
            if not has_error:
                models.Permission.objects.bulk_create(object_list, batch_size=100)  # 批量添加
        else:
            generate_formset = formset

    if request.method == "POST" and post_type == "update":  # 批量更新
        formset = update_formset_class(data=request.POST)
        if formset.is_valid():
            post_row_list = formset.cleaned_data
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                permission_id = row_dict.pop("id")
                try:
                    row_object = models.Permission.objects.filter(pk=permission_id).first()
                    for k, v in row_dict.items():
                        setattr(row_object, k, v)
                    row_object.validate_unique()
                    row_object.save()
                except Exception as e:
                    formset.errors[i].update(e)
                    update_formset = formset
        else:
            update_formset = formset

    # 1.获取项目中，所有的URL
    all_url_dict = get_all_url_dict()
    router_name_set = set(all_url_dict.keys())

    # 2. 获取数据库中所有的url
    permissions = models.Permission.objects.all().values("id", "title", "name", "url", "menu_id", "pid_id")

    permission_dict = OrderedDict()
    permission_name_set = set()

    for row in permissions:
        permission_dict[row.get("name")] = row
        permission_name_set.add(row.get("name"))
    # permission_name_set = set(permission_dict.keys())
    # 这个循环主要是为了，进行更新操作的时候。有可能自动发现和数据库中 name 一样而url不一样时。强制更改一下
    # 让用户去自己去检查一下。 到底要使用 那个url。 需要用户自己手动填写
    for name, value in permission_dict.items():
        router_row = all_url_dict.get(name)
        if not router_row:
            continue
        if value.get("url") != router_row.get("url"):
            value["url"] = "路由和数据库中不一致，请检查。并填写正确的  url！！"

    # 3. 应该要 添加，删除，修改的权限有哪些

    # 3.1 计算出应该添加的name 并生成 formset (自动发现有的，数据库没有的。所以要循环的是 自动发现查询出的字典)
    if not generate_formset:
        generate_name_list = router_name_set - permission_name_set  # 增加列表
        generate_formset = generate_formset_class(
            initial=[row_dict for name, row_dict in all_url_dict.items() if name in generate_name_list])

    # 3.2 计算出，应该删除的name，(数据库有的，自动发现 没有的。所以要循环的是 数据库查询出的字典)
    delete_name_list = permission_name_set - router_name_set  # 删除列表
    #  页面展示时 不需要删除的formset 只提供一个删除按钮就好
    delete_row_list = [row_dict for name, row_dict in permission_dict.items() if name in delete_name_list]

    # 3.3 计算出应该更新的name (数据库有的，自动发现有的。所以要循环的是 数据库查询出的字典)
    if not update_formset:
        update_name_list = permission_name_set & router_name_set  # 更新列表
        update_formset = update_formset_class(
            initial=[row_dict for name, row_dict in permission_dict.items() if name in update_name_list])

    return render(request, "rbac/multi_permission.html",
                  {"generate_formset": generate_formset,
                   "delete_row_list": delete_row_list,
                   "update_formset": update_formset},
                  )


def multi_permissions_del(request, pk):
    '''
    删除操作， 需要给与用户提示。
    :param reuqest:
    :param pk:  要删除的权限id
    :return:
    '''
    origin_url = memory_reverse(request, "rbac:multi_permissions")
    permission_queryset = models.Permission.objects.filter(pk=pk)
    if not permission_queryset:
        return HttpResponse("菜单不存在")
    if request.method == "POST":
        permission_queryset.delete()
        return redirect(origin_url)
    return render(request, "rbac/delete.html", {"cancel": origin_url})


def distribute_permission(request):
    '''
    权限分配
    :param request:
    :return:
    '''
    user_model_class = import_string(settings.RBAC_USER_MODEL_ClASS)
    user_id = request.GET.get('uid')
    role_id = request.GET.get('rid')
    # user_obj = models.UserInfo.objects.filter(pk=user_id).first()
    user_obj = user_model_class.objects.filter(pk=user_id).first()  # 有业务app时,使用业务app中的UserInfo表
    role_obj = models.Role.objects.filter(pk=role_id).first()

    if request.method == "POST" and request.POST.get("type") == "role":
        role_id_list = request.POST.getlist("roles")
        if not user_obj:
            return HttpResponse("请选择用户，不要自己添加input标签。烦得很")
        user_obj.roles.set(role_id_list)  # 通过用户找到 roles 然后set 向他们的关系表。 更新数据
    if request.method == "POST" and request.POST.get("type") == "permission":
        permission_id_list = request.POST.getlist("permissions")
        if not user_obj or not role_obj:
            return HttpResponse("请选择用户，不要自己添加input标签。烦得很")
        role_obj.permissions.set(permission_id_list)

    if not user_obj:
        user_id = None

    if not role_obj:
        role_id = None

    # 获取当前用户所拥有的角色. 进行默认选择
    if user_id:
        user_has_role = user_obj.roles.all().values("id")
    else:
        user_has_role = []
    user_has_role_dict = {item["id"]: None for item in user_has_role}

    # 如果选中了角色，优先显示选中的角色，拥有的权限。 如果没有选择角色，才显示用户的所有权限
    if role_obj:
        user_has_permissions = role_obj.permissions.all()
        user_has_permissions_dict = {item.id: None for item in user_has_permissions}
    elif user_obj:
        user_has_permissions = user_obj.roles.values("permissions__id").distinct()  # 获取当前用户所拥有的所有权限
        user_has_permissions_dict = {item["permissions__id"]: None for item in user_has_permissions}
    else:
        user_has_permissions_dict = {}

    all_user_queryset = user_model_class.objects.all()
    all_role_queryset = models.Role.objects.all()

    # 所有的一级菜单
    all_menu_list = models.Menu.objects.values("mid", "title")
    # 所有的二级菜单
    all_second_menu_queryset = models.Permission.objects.filter(menu_id__isnull=False).values("id", "title", "menu_id")
    # 所有的不是二级菜单的权限
    all_permission_queryset = models.Permission.objects.filter(menu_id__isnull=True).values("id", "title", "pid_id")

    all_menu_dict = {}
    for item in all_menu_list:
        item["children"] = []
        all_menu_dict[item.get("mid")] = item

    all_second_menu_dict = {}
    for row in all_second_menu_queryset:
        row["children"] = []
        all_second_menu_dict[row.get("id")] = row

        menu_id = row.get("menu_id")
        all_menu_dict.get(menu_id).get("children").append(row)

    for row in all_permission_queryset:
        pid_id = row.get("pid_id")
        if not pid_id:
            continue
        all_second_menu_dict.get(pid_id).get("children").append(row)

    return render(request, "rbac/distribute_permissions.html",
                  {"all_user_list": all_user_queryset,
                   "all_role_list": all_role_queryset,
                   "all_menu_queryset": all_menu_list,
                   "user_id": user_id,
                   "role_id": role_id,
                   "user_has_role_dict": user_has_role_dict,
                   "user_has_permissions_dict": user_has_permissions_dict})
