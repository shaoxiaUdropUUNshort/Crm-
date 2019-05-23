#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/18
import functools
from types import FunctionType
from django.urls import re_path
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, redirect, reverse
from django.utils.safestring import mark_safe
from django import forms
from stark.utils.pagination import Pagination
from django.db.models import Q
from django.db.models import ForeignKey, ManyToManyField


class SearchGroupRow(object):
    def __init__(self, queryset_or_list, option, title, query_dict):
        self.query_dict = query_dict  # request.GET
        self.title = title
        self.option = option
        self.queryset_or_list = queryset_or_list

    def __iter__(self):
        '''默认显示。 用户可以自定制'''
        yield "<div class='whole'>"
        yield self.title
        yield "</div>"
        yield "<div class='others'>"
        total_query_dict = self.query_dict.copy()  # 做一次copy 不对原数据。在修改时造成影响
        total_query_dict._mutable = True
        origin_value_list = self.query_dict.getlist(self.option.field)
        if not origin_value_list:
            yield "<a class='active' href='?%s'>全部</a>" % total_query_dict.urlencode()
        else:
            total_query_dict.pop(self.option.field)
            yield "<a href='?%s'>全部</a>" % total_query_dict.urlencode()

        for item in self.queryset_or_list:
            text = self.option.get_text_func(item)
            # print(text)

            # 需要request.GET
            query_dict = self.query_dict.copy()  # 做一次copy 不对原数据。在修改时造成影响
            query_dict._mutable = True  # QueryDict 默认不允许被修改。 添加这句就可以被修改了
            # 需要文本 背后的 id
            value = str(self.option.get_value_func(item))
            # print(value, type(value))
            # origin_value_list = query_dict.getlist(self.option.field)
            if not self.option.is_multi:  # 默认单选
                query_dict[self.option.field] = value
                if value in origin_value_list:
                    query_dict.pop(self.option.field)
                    yield "<a class='active' href='?%s'>%s</a>" % (query_dict.urlencode(), text)
                else:
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(), text)
            else:
                multi_query_list = query_dict.getlist(self.option.field)
                if value in multi_query_list:
                    multi_query_list.remove(value)  # 如果当前值，已经存在于请求列表中，就移除
                    query_dict.setlist(self.option.field, multi_query_list)  # 更新 query_dict 中。 与键相对应的列表
                    yield "<a class='active' href='?%s'>%s</a>" % (query_dict.urlencode(), text)
                else:
                    multi_query_list.append(value)  # 否则，就添加
                    query_dict.setlist(self.option.field, multi_query_list)
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(), text)

        yield "</div>"


class Option(object):
    '''使用组合搜索， 想要一些自己的搜索条件。 可扩展可继承'''

    def __init__(self, field, is_multi=False, db_condition=None, text_func=None, value_func=None):
        '''
        :param filed:  组合搜索关联的字段
        :param is_multi:  是否支持，组合搜索的多选。
        :param db_condition:  数据库关联查询时查询的条件
        :param text_func: 自定制函数用于，页面组合搜索的文本和样式
        :param value_func: 自定制函数用于，页面组合搜索时。可以指定 a 标签的 herf 属性。 默认使用每个字段的id
        '''
        self.is_multi = is_multi
        self.field = field
        self.db_condition = db_condition
        self.text_func = text_func
        self.value_func = value_func
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition

        self.is_choice = False  # 用于判断field对象里面是一个 choice列表 or 外键的queryset

    def get_value_func(self, field_obj):
        '''
        获取对象 id 的函数。(从)
        :param field_obj:  (1, "男")  or model对象
        :return:
        '''
        if self.value_func:
            return self.text_func(field_obj)

        if self.is_choice:
            return field_obj[0]
        return field_obj.pk

    def get_text_func(self, field_obj, ):
        '''
        获取文本，的函数。(从)
        :param field_obj:  (1, "男")  or model对象
        :return:
        '''
        if self.text_func:
            return self.text_func(field_obj)

        if self.is_choice:
            return field_obj[1]
        return str(field_obj)

    def get_db_condition(self, request, *args, **kwargs):
        '''预留继承后的重写函数， 重写后，次基类中的该方法，将被覆盖。 默认返回的是开发者输入的值。'''
        '''重写后， 可根据，前端的返回值，进行一定的判断'''
        return self.db_condition

    def get_queryset_or_list(self, model_class, request, *args, **kwargs):
        '''根据字段去获取数据库关联的数据'''

        # 根据gender或者classes字符串，组自己对应的model类中，找到字段对象，再根据对象，获取关联的数据
        field_obj = model_class._meta.get_field(self.field)  # 固定用法mate 类，中的get_field() 就可以根据字符串获取对应的对象
        title = field_obj.verbose_name
        # 对field_obj 的类型做判断。 来确定他是一个 choice 还是一个 foreignkey 外键
        if isinstance(field_obj, ForeignKey) or isinstance(field_obj, ManyToManyField):
            # 获取关联表中的， 数据   django1.0 版本使用 field_obj.rel.model.objects.all()
            db_condition = self.get_db_condition(request, *args, **kwargs)
            return SearchGroupRow(field_obj.related_model.objects.filter(**db_condition), self, title, request.GET)
            # 这里得到的是 Queryset 类型
        else:
            # 获取 choice 的数据 field_obj.choices
            self.is_choice = True
            return SearchGroupRow(field_obj.choices, self, title, request.GET)  # 这里得到的是  tuple 类型


class StarkModelForm(forms.ModelForm):
    '''
    因为，太多的地方需要使用， __init__ 初始化方式。来对每个标签添加 class="form-control" 所以搞个基类让
    要进行， 这部操作的 类去继承，
    '''

    def __init__(self, *args, **kwargs):
        super(StarkModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class StarkForm(forms.Form):
    '''
    因为，太多的地方需要使用， __init__ 初始化方式。来对每个标签添加 class="form-control" 所以搞个基类让
    要进行， 这部操作的 类去继承，
    '''

    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class StartHandler(object):
    list_display = []
    check_list_template = None  # 自定制的，查看模板路径。 默认使用stark指定的。 也可以跟进此参数自己指定
    edit_template = None  # 自定制，编辑的使用模板
    add_template = None  # 自定制，添加的使用模板
    del_template = None  # 自定制删除的使用模板

    def __init__(self, site, model_class, prve):
        self.site = site
        self.model_class = model_class
        self.prev = prve
        self.request = None

    has_add_btn = True  # 指定配置，默认显示。 用户在子类中，自定制是否显示，添加按钮

    def get_add_btn(self, request, *args, **kwargs):
        '''预留钩子，子类中重写该方法。 根据权限的判断是否显示添加按钮'''
        if self.has_add_btn:
            # 根据别名反向生成， URL
            add_url = self.memory_url(self.get_add_url_name, *args, **kwargs)
            return "<a class='btn btn-primary' href='%s'>添加</a>" % add_url
        return None

    # 用于在 a 标签。 携带本次GET 请求参数
    def memory_url(self, get_url_name, *args, **kwargs):
        '''用于反向生成url， 并且携带，get请求的参数，跳转到下一个网页'''
        name = "%s:%s" % (self.site.namespace, get_url_name)
        base_url = reverse(name, args=args, kwargs=kwargs)
        # 记录原搜索条件
        if not self.request.GET:
            url = base_url
        else:
            param = self.request.GET.urlencode()  # 获取到GET请求的，所有的参数。 ?page=1&age=20
            new_query_dict = QueryDict(mutable=True)
            new_query_dict["_filter"] = param
            url = "%s?%s" % (base_url, new_query_dict.urlencode())
        return url

    # 用于 跳转会原页面时，解析出 GET 请求的参数。并拼接
    def memory_reverse(self, get_url_name, *args, **kwargs):
        name = "%s:%s" % (self.site.namespace, get_url_name)
        url = reverse(name, args=args, kwargs=kwargs)
        origin_params = self.request.GET.get("_filter")
        if origin_params:
            url = "%s?%s" % (url, origin_params)
        return url

    # 对于这两个用来，解析URL的函数来说，request 这个参数。可加可不加。看自己的需求吧！

    # 用于用户自定制， chackbox 复选框！ 进行批量操作使用
    def display_checkbox(self, obj=None, is_header=None, *args, **kwargs):
        '''
        checkbox 列的显示
        :param obj:
        :param is_header:
        :return:
        '''
        if is_header:
            return "选择"
        return mark_safe('<input type="checkbox" name="pk" value="%s">' % obj.pk)

    # 用于用户自定制， 是否显示编辑按钮, 和显示的样式
    def display_edit(self, obj=None, is_header=None, *args, **kwargs):
        '''
        自定义页面，显示的列，(表头和内容)
        :param obj:   数据库中每一行记录的 model对象
        :param is_header:  判断是否为表头
        :return:
        '''
        if is_header:
            return "编辑"
        # return mark_safe("<a href='%s'>编辑</a>" %
        #                  self.memory_url(get_url_name=self.get_edit_url_name, pk=obj.pk))
        return mark_safe(
            "<a href='%s'><i class='fa fa-edit' aria-hidden='true' style='position:relative;top:1px;'></i></a>" \
            % (self.memory_url(get_url_name=self.get_edit_url_name, pk=obj.pk)))

    # 用于用户自定制， 是否显示删除按钮
    def display_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "删除"
        # return mark_safe("<a href='%s'>删除</a>" %
        #                  self.memory_url(get_url_name=self.get_del_url_name, pk=obj.pk))
        return mark_safe("<a href='%s' style='color:#f44336'><i class='fa fa-trash-o' aria-hidden='true'></i></a>" \
                         % self.memory_url(get_url_name=self.get_del_url_name, pk=obj.pk))

    # 将编辑和删除操作，放到一列中
    def display_edit_and_display_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "操作"
        return mark_safe(
            "<a href='%s'><i class='fa fa-edit' aria-hidden='true' style='position:relative;top:1px;'></i></a> | "
            "<a href='%s' style='color:#f44336'><i class='fa fa-trash-o' aria-hidden='true'></i></a>"
            % (self.memory_url(get_url_name=self.get_edit_url_name, pk=obj.pk),
               self.memory_url(get_url_name=self.get_del_url_name, pk=obj.pk)))

    # 用户自定制，是否使用该功能。 只要在子类中的 action_list=[StarkHandler.multi_delete] 就可以使用该功能
    def action_multi_delete(self, request, *args, **kwargs):
        '''批量删除( 如果想要定制，执行成功后的返回值，那么就为这个函数，设置返回值就可以)'''
        self.model_class.objects.filter(pk__in=request.POST.getlist("pk")).delete()
        # return redirect("http://www.baidu.com")
    action_multi_delete.text = "批量删除"

    # 用户自定制，是否使用该功能。 只要在子类中的 action_list=[StarkHandler.multi_init] 就可以使用该功能
    def action_multi_init(self, request, *args, **kwargs):
        '''批量初始化'''
        pass
    action_multi_init.text = "批量初始化"

    # 如果向模板中，传递一个函数的话，他就会自动的执行一边。 从而前端的页面也因为这个原因，拿不到 text 的值。
    # 所以就需要在后端把这个 action_list 处理成一个字典。这件事由基类完成 {func.__name__: func.text for func in action_list}

    def get_list_display(self, request, *args, **kwargs):
        '''
        获取不同用户登录时， 页面应该显示的列. 使用时在子类中，重写该方法，指定list_display 要包含哪些值
        我在这里默认了，让他们都自带有，编辑和删除的功能。 如果不需要也可以自己改
        :return:
        '''
        value = []
        if self.list_display:  # 默认让表，拥有编辑删除功能。 也可以自己制定。
            # 如果想根据权限来， 那就重写该方法。 也可以改该源码。
            value.extend(self.list_display)
            # value.extend([ StartHandler.display_edit, StartHandler.display_del])  # 分成两列使用这个
            value.append(type(self).display_edit_and_display_del)  # 合成一列使用这个
        return value

    ordered_list = []  # 排序规则由 用户指定。
    def get_ordered_list(self):
        return self.ordered_list or ["-id", ]  # 默认使用 id 进行排序

    search_list = []  # 方便，用户自己定制。关键字搜索的条件，和如果用户不配置，页面不显示搜索框
    def get_search_list(self):
        return self.search_list

    search_group = []  # 方便，用户自己定制。组合搜索搜索的条件，和如果用户不配置，页面不显示组合搜索
    def get_search_group(self):
        return self.search_group

    def get_search_group_condition(self, request):
        condition = {}
        for option in self.get_search_group():
            if option.is_multi:
                value_list = request.GET.getlist(option.field)  # "depart":[1, 2, 3]
                if not value_list:  # 如果这个值为空，那就说明，用户没有查询这个条件， 直接跳过就好
                    continue
                condition["%s__in" % option.field] = value_list
            else:
                value = request.GET.get(option.field)  # "depart":[1]
                if not value:  # 如果这个值为空，那就说明，用户没有查询这个条件， 直接跳过就好
                    continue
                condition[option.field] = value
        return condition

    def get_queryset(self, request, *args, **kwargs):
        '''对要查询的内容做一次扩展，子类中根据需求扩展,(我这里用于公户私户的数据的筛选)'''
        return self.model_class.objects

    per_page = 10  # 默认每页显示，多少数据。 也可在子类中，自行定制
    def check_list_view(self, request, *args, **kwargs):
        '''
        列表查看页面
        :param request:
        :return:
        '''
        list_display = self.get_list_display(request, *args, **kwargs)  # 页面要显示的列 self.list_display  示例：['name', 'age', 'depart']

        # ####################1. 处理 Action ######################
        action_list = self.get_action_list()
        action_dict = {func.__name__: func.text for func in action_list}  # func.__name__获取函数名， func.text获取函数文本
        if request.method == "POST":
            action_func_name = request.POST.get("action")
            if action_func_name and action_func_name in action_dict:  # 前端发送过来的name 必须要在 action_dict中。
                action_respons = getattr(self, action_func_name)(request, *args, **kwargs)
                if action_respons:
                    return action_respons

        # #######################2. 处理表头##############################
        # 1. 制作表头， 就是每张表中，每个字段写的 verbose_name.。 如何获取到这个值呢？
        # self.model_class._meta.get_field('name').verbose_name
        header_list = []  # 表头
        if list_display:
            for key_or_func in list_display:
                if isinstance(key_or_func, FunctionType):  # 判断当前参数， 是一个字符串还是一个函数。
                    verbose_name = key_or_func(self, obj=None, is_header=True, *args, **kwargs)
                else:
                    verbose_name = self.model_class._meta.get_field(key_or_func).verbose_name
                header_list.append(verbose_name)
        else:
            header_list.append(self.model_class._meta.model_name)

        # ##################3. 获取排序，和， 模糊搜索的条件######################
        order_list = self.get_ordered_list()  # 排序方式  默认 使用 id 进行正向排序
        search_list = self.get_search_list()  # 搜索的条件 ["name_contains", "email"]
        '''
        1. 如果 search_list 为空， 则不显示 搜索框
        2. 获取用户输入的 关键字
        3. 构造搜索条件
        '''
        search_value = self.request.GET.get("q", "")  # 获取用户发送过来的关键字，如果没有 q 这个参数。 就返回 ""
        conn = Q()
        conn.connector = "OR"  # 让添加进来的条件， 做 or 判断
        if search_value:  # 接收到了用户的搜索，才进行模糊查询。 否则啥都不干
            for item in search_list:
                conn.children.append((item, search_value))

        # ###############4. 从数据库过滤出想要的数据##################
        # 计算总数量，和 表格显示内容时，都需要，就提取出来了
        search_group_condition = self.get_search_group_condition(request)
        prev_queryset = self.get_queryset(request, *args, **kwargs)
        query_set = prev_queryset.filter(conn).filter(**search_group_condition).distinct().order_by(*order_list)

        # ####################5. 处理分页######################
        '''1.根据用户访问页面，计算出索引的位置， 比如 page=3
            2. 生成html页码
        '''
        all_count = query_set.count()  # 得到查询到的数据的总数量
        query_params = request.GET.copy()  # page=1&level=2
        query_params._mutable = True  # request.get中的值默认是不能被修改的。加上这句代码就可以修改了
        pager = Pagination(
            current_page=request.GET.get("page"),  # 用户访问的当前叶
            all_count=all_count,  # 数据库一共有多少数据
            base_url=request.path_info,  # 所在的url 就是 ?page=1 之前的URL
            # 用于保留，用户的请求信息,比如 level=2 被用户先选中。 那么分页后。因为查询的东西少了，分页也应该想要的减少,
            # 但是level=2这个， 请求的信息！不能因为。分页的原因。而减少。
            query_params=query_params,
            per_page=self.per_page,  # 每页显示多少数据。
        )

        # ##################5. 处理表格######################
        data_list = query_set[pager.start:pager.end]  # 对得到的内容。 进行切片获取，并展示到页面上

        body_list = []
        for row in data_list:
            row_list = []
            if list_display:
                for key_or_func in list_display:
                    if isinstance(key_or_func, FunctionType):
                        # 这里is_header=False  obj=row（数据库中循环的每一行的对象）
                        row_list.append(key_or_func(self, obj=row, is_header=False, *args, **kwargs))
                    else:
                        row_list.append(getattr(row, key_or_func))
            else:
                row_list.append(row)
            body_list.append(row_list)

        # ################6. 处理添加按钮######################
        add_btn = self.get_add_btn(request, *args, **kwargs)  # request还用不到。加上只是以放万一

        # ####################7. 处理组合搜索###################
        search_group_row_list = []  # 修改之后这里
        search_group = self.get_search_group()  # ["gender", "classes", "depart"]
        for option in search_group:
            queryset_or_list = option.get_queryset_or_list(self.model_class, request)
            search_group_row_list.append(queryset_or_list)

        return render(request, self.check_list_template or "stark/changelist.html",
                      {"header_list": header_list, "data_list": data_list,
                       "body_list": body_list,
                       "pager": pager,
                       "add_btn": add_btn,
                       "search_list": search_list,
                       "search_value": search_value,
                       "action_dict": action_dict,
                       "search_group_row_list": search_group_row_list})

    action_list = []  # 批量函数，添加列表
    def get_action_list(self):
        return self.action_list

    model_form_class = None  # 预留自定义form对象的接口.(这个针对的是 添加和编辑窗口) 查看请自行添加
    def get_model_form_class(self, is_add, request, pk, *args, **kwargs):
        '''
        定制 添加编辑页面。 model_form的定制
        :param is_add:
        :return:
        '''
        if self.model_form_class:
            return self.model_form_class

        class DynamicModelForm(StarkModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"

        return DynamicModelForm

    # 预留的 form 保存。自定制接口
    def save(self, request, form, is_update, *args, **kwargs):
        '''
        在使用 ModelForm 保存数据之前，预留的钩子方法
        :param form:   每一个 model_class 自己的 form 对象
        :param is_update: 传参时指定，是添加保存，还是更新的保存
        :param request:  获取当前用户的一些信息
        :param  *args, **kwargs: 只是为了，可能会有的参数。会传递进来！以便于日后使用，和扩展
        :return:
        '''
        form.save()

    def add_view(self, request, *args, **kwargs):
        '''
        添加页面
        :param request:
        :return:
        '''

        model_form_class = self.get_model_form_class(True, request, None, *args, **kwargs)
        if request.method == "GET":
            form = model_form_class()
            return render(request, self.add_template or "stark/change.html", {"form": form})
        form = model_form_class(data=request.POST)
        if request.method == "POST":
            if form.is_valid():
                response = self.save(request, form, False, *args, **kwargs)
                return response or redirect(self.memory_reverse(self.get_list_url_name, *args, **kwargs))
            return render(request, self.add_template or "stark/change.html", {"form": form})

    def get_change_object(self, request, pk, *args, **kwargs):
        '''扩展，过滤条件'''
        return self.model_class.objects.filter(pk=pk).first()

    def change_view(self, request, pk, *args, **kwargs):

        '''
        编辑页面
        :param request:
        :return:
        '''
        current_change_obj = self.get_change_object(request, pk, *args, **kwargs)
        if not current_change_obj:
            return HttpResponse("要修改的页面不存在，请重新选择")

        model_form_class = self.get_model_form_class(False, request, pk, *args, **kwargs)
        if request.method == "GET":
            form = model_form_class(instance=current_change_obj)
            return render(request, self.edit_template or "stark/change.html", {"form": form})
        form = model_form_class(data=request.POST, instance=current_change_obj)
        if request.method == "POST":
            if form.is_valid():
                response = self.save(request, form, True, *args, **kwargs)
                return response or redirect(self.memory_reverse(self.get_list_url_name, *args, **kwargs))
            return render(request, self.edit_template or "stark/change.html", {"form": form})
        return HttpResponse("编辑页面")

    # def get_delete_object(self, request, pk, *args, **kwargs):
    #     '''扩展，过滤条件'''
    #     return self.model_class.objects.filter(pk=pk)
    #
    # def delete_view(self, request, pk, *args, **kwargs):
    #     '''
    #     删除页面
    #     :param request:
    #     :return:
    #     '''
    #     origin_url = self.memory_reverse(get_url_name=self.get_list_url_name, *args, **kwargs)
    #     current_model_obj = self.get_delete_object(request, pk, *args, **kwargs)
    #     if not current_model_obj:
    #         return HttpResponse("要修改的记录不存在，请重新选择")
    #     if request.method == "POST":
    #         current_model_obj.delete()
    #         return redirect(origin_url)
    #     return render(request, self.del_template or "stark/delete.html", {"cancel": origin_url})

    def get_delete_object(self, request, pk, *args, **kwargs):
        '''扩展删除，过滤条件'''
        queryset = self.model_class.objects.filter(pk=pk)
        if not queryset:
            return HttpResponse("没有记录不能删除")
        queryset.delete()

    def delete_view(self, request, pk, *args, **kwargs):
        '''
        删除页面
        :param request:
        :return:
        '''
        origin_url = self.memory_reverse(get_url_name=self.get_list_url_name, *args, **kwargs)
        if request.method == "POST":
            response = self.get_delete_object(request, pk, *args, **kwargs)
            return response or redirect(origin_url)
        return render(request, self.del_template or "stark/delete.html", {"cancel": origin_url})

    def get_url_name(self, param):
        '''
        判断是否有后缀  prev。 进行拼接URL的别名
        :param param: 页面后缀(list, add, change, del)
        :return:
        '''
        # 获取每个model_class类。所在的app_name 和 他自己的 表名称model_name
        app_label, model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        if self.prev:
            return "%s_%s_%s_%s" % (app_label, model_name, self.prev, param)  # app01/userinfo/prev/list/
        return "%s_%s_%s" % (app_label, model_name, param)  # app01/userinfo/list/

    @property
    def get_list_url_name(self):
        '''获取列表页面URL 的name'''
        return self.get_url_name("list")

    @property
    def get_add_url_name(self):
        '''获取添加页面URL 的name'''
        return self.get_url_name("add")

    @property
    def get_edit_url_name(self):
        '''获取修改页面URL 的name'''
        return self.get_url_name("change")  # app01_userinfo_change

    @property
    def get_del_url_name(self):
        '''获取删除页面URL 的name'''
        return self.get_url_name("del")

    def wrapper(self, func):
        @functools.wraps(func)  # 保留原函数的 原信息
        def inner(request, *args, **kwargs):  # 这个inner 就是，我的每一个视图函数了！
            self.request = request
            return func(request, *args, **kwargs)
        return inner

    # 用户可自定制，该函数。 指定需要显示，那种url 。增加或删除。
    def get_urls(self):
        partterns = [
            re_path(r"list/$", self.wrapper(self.check_list_view), name=self.get_list_url_name),
            re_path(r"add/$", self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r"change/(?P<pk>\d+)/$", self.wrapper(self.change_view), name=self.get_edit_url_name),
            re_path(r"del/(?P<pk>\d+)/$", self.wrapper(self.delete_view), name=self.get_del_url_name),
        ]

        partterns.extend(self.extra_url())
        return partterns

    # 只适用于增加url
    def extra_url(self):
        '''用于让用户自己去指定，增加的url '''
        return []


class StartSite(object):
    def __init__(self):
        self._registry = []
        self.app_name = "stark"
        self.namespace = "stark"

    def register(self, model_class, handler_class=None, prev=None):
        '''
        :param model_class:  是model中数据库相关类。 接受一个类而不是对象
        :param handler_class: 处理请求的视图函数，所在的类
        :param prev:  生成url 的前缀
        :return:
        '''

        if handler_class is None:
            handler_class = StartHandler  # 做个默认的Handler

        self._registry.append(
            {'model_class': model_class, "handler": handler_class(self, model_class, prev), "prev": prev})
        '''
        [
            {'model_class':models.Depart, "handler":DepartHandler(models.Depart, prev),"prev": prev},
            {'model_class':models.UserInfo, "handler":UserInfoHandler(models.UserInfo, prev),"prev": prev},
            {'model_class':models.Host, "handler":HostHandler(models.Host, prev),"prev": prev},
        ]
        '''

    def get_urls(self):
        partterns = []
        for item in self._registry:
            model_class = item["model_class"]
            handler = item["handler"]
            prev = item["prev"]
            # 获取当前model_class所在的app名字 # 获取当前model_class的类名，小写
            app_label, model_name = model_class._meta.app_label, model_class._meta.model_name
            if prev:
                partterns.append(
                    re_path(r"%s/%s/%s/" % (app_label, model_name, prev), (handler.get_urls(), None, None)))
            else:
                partterns.append(re_path(r"%s/%s/" % (app_label, model_name), (handler.get_urls(), None, None)))
        return partterns

    @property
    def urls(self):
        '''模拟include的返回值'''
        return (self.get_urls(), self.app_name, self.namespace)


def get_choice_text(title, field):
    '''
    对于 Stark组件中定义列时， choice如果想要显示中文信息，调用此方法即可。
    :param title:   希望页面上显示的表头
    :param field:  字段名称
    :return:
    '''

    def inner_choice(self, obj=None, is_header=None, *args, **kwargs):
        '''
        :param self:
        :param obj:  StarkHandler 里面列表视图函数 中 循环出的每一个 model对象
        :param is_header:
        :return:
        '''
        if is_header:
            return title
        method = "get_%s_display" % field
        return getattr(obj, method)()  # 从model对象中，根据这个字符串。找到这个方法。 并执行。 拿到中文结果后， 返回

    return inner_choice


def get_datetime_text(title, field,  date_format="%Y-%m-%d"):
    '''
    对于 Stark组件中定义列时，获取时间格式的数据。可定制化.
    :param title:   希望页面上显示的表头
    :param field:  字段名称
    :param format:  要格式化的时间格式
    :return:
    '''

    def inner_datetime(self, obj=None, is_header=None, *args, **kwargs):
        '''
        :param self:
        :param obj:  StarkHandler 里面列表视图函数 中 循环出的每一行记录 model对象 <class 'web.models.ClassList'>
        :param is_header:  标题名称
        :return:
        '''
        if is_header:
            return title
        # print(type(obj))  # <class 'web.models.ClassList'>
        datetime_value = getattr(obj, field)  # 从obj这个类中，根据这个字符串。 拿到field字段的数据
        if not datetime_value:
            return "-----------"
        return datetime_value.strftime(date_format)  # 数据的格式，看需求
    return inner_datetime


def get_manytomany_text(title, field):
    '''
    对于 Stark组件中定义列时，显示 manytomany 外键文本的信息
    :param title:   希望页面上显示的表头
    :param field:  字段名称
    :return:
    '''

    def inner_manytomany(self, obj=None, is_header=None):
        '''
        :param self:
        :param obj:  StarkHandler 里面列表视图函数 中 循环出的每一行记录 model对象 <class 'web.models.ClassList'>
        :param is_header:  标题名称
        :return:
        '''
        if is_header:
            return title
        # 从每一行数据中(这也是一个类), 找到他的 field 属性。 而对于多对多的外键字段。拿到的其实是 UserInfo这张模型表, 加上.all() 就可以了
        # <class 'django.db.models.fields.related_descriptors.create_forward_many_to_many_manager.<locals>.ManyRelatedManager'>
        queryset = getattr(obj, field).all()
        if not queryset:
            return "-----------"
        text_list = [str(row) for row in queryset]
        return ",".join(text_list)
    return inner_manytomany


site = StartSite()
