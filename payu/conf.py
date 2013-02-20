# -*- coding: utf-8 -*-

from django.conf import settings

_ACTION_URL = 'https://secure.payu.ru/order/lu.php'

TEST = getattr(settings, 'PAYU_TEST', True)
VAT = getattr(settings, 'PAYU_VAT', 0)
LANGUAGE = getattr(settings, 'PAYU_LANGUAGE', 'RU')
CURRENCY = getattr(settings, 'PAYU_CURRENCY', 'RUB')
ACTION_URL = getattr(settings, 'PAYU_ACTION_URL', _ACTION_URL)


BACK_REF = settings.PAYU_BACK_REF
MERCHANT = settings.PAYU_MERCHANT
MERCHANT_KEY = settings.PAYU_KEY