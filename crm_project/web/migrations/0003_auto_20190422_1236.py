# Generated by Django 2.1.7 on 2019-04-22 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_userinfo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='classes',
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='nickname',
            field=models.CharField(max_length=32, verbose_name='昵称'),
        ),
    ]
