# -*- coding: utf-8 -*-

from payu.conf import ACTION_URL


def payu(request):
    return {
        'PAYU_ACTION_URL': ACTION_URL,
    }