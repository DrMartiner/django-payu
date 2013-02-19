# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import ipn

urlpatterns = patterns('',
    url(r'^ipn/$',ipn ,name='payu_ipn'),
)
