#!usr/bin/env python
# -*- coding:utf-8
"""
@author:alvin
@file: urls.py
@time: 2019/08/13
"""

from django.urls import path
from utils import views

urlpatterns = [
    path("success",views.test_success),
    path("failed",views.test_failed)
]
