# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('payu.views',
    url(r'^ipn/$', 'ipn', name='payu_ipn'),
)
