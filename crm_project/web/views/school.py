#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/22
from stark.servers.start_v1 import StartHandler
from .base import PermissionHandler


class SchoolHandler(PermissionHandler, StartHandler):
    # list_display = ["title", StartHandler.display_edit, StartHandler.display_del]
    list_display = ["title"]


