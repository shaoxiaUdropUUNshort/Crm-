from django.db import models


class Permission(models.Model):
    """
    权限表  一级菜单的表
    """
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(verbose_name='含正则的URL', max_length=128)
    name = models.CharField(verbose_name="权限别名", max_length=32, unique=True)
    menu = models.ForeignKey(verbose_name="所属菜单", to="Menu", null=True, blank=True, on_delete=models.CASCADE)
    pid = models.ForeignKey(verbose_name="关联权限", help_text="对于非菜单权限，需要确定当前权限归属于哪一个，父权限",
                            to="Permission", null=True, blank=True, on_delete=models.CASCADE, )

    def __str__(self):
        return self.title


class Menu(models.Model):
    mid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='一级菜单标题', max_length=32)
    icon = models.CharField(verbose_name="图标", max_length=32, )

    def __str__(self):
        return self.title


class Role(models.Model):
    """角色"""
    title = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='拥有的所有权限', to='Permission', blank=True)

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    """
    用户表
    """
    name = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)
    email = models.CharField(verbose_name='邮箱', max_length=32)
    # roles = models.ManyToManyField(verbose_name='拥有的所有角色', to='Role', blank=True, null=True)
    roles = models.ManyToManyField(verbose_name='拥有的所有角色', to=Role, blank=True)
    # 一定要记住， 如果被继承了！ 在别的地方创建关联关系的时候。 会在别的地方找 Role 这张表。
    # 但是 别的地方肯定是没有的， 所有 在制定表的时候，直接把表对象放进去 to=Role 不要再使用 to="Role"
    # 这样在继承的时候， 会连带这Role这张表的内存地址，一起继承过去。 否则，会报错。 说在你的业务中找不到 Role 这张表

    class Meta:
        # django以后再做数据库迁移的时候， 不再为UserInfo类，创建相关的表以及结构
        # 此类 可以当作 "父类", 被其他 model类继承。
        abstract = True

    # def __str__(self):
    #     return self.name
