#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "nothing"
# Date: 2019/4/22
import hashlib


def creatr_md5(origin):
    '''
    MD5加密，
    :param origin:  要被加密的参数
    :return:
    '''
    # ha = hashlib.md5(b"asdasdasdasdasd")  # 也可以在这里进行加盐
    ha = hashlib.md5()  # 也可以在这里进行加盐
    ha.update(origin.encode("utf-8"))
    return ha.hexdigest()
