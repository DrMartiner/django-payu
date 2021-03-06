# -*- coding: utf-8 -*-

import hmac

import re
from datetime import datetime
from django import forms
from payu.models import PayUIPN
from payu.conf import MERCHANT, MERCHANT_KEY, TEST, LANGUAGE, CURRENCY, BACK_REF


class ValueHiddenInput(forms.HiddenInput):
    """
    Widget that renders only if it has a value.
    Used to remove unused fields from PayPal buttons.
    """

    def render(self, name, value, attrs=None):
        m = re.match(r'^ORDER_(\d+)_(\d+)$', name)
        if m is not None:
            name = 'ORDER_%s[]' % ['PNAME', 'PGROUP', 'PCODE', 'PINFO', 'PRICE', 'PRICE_TYPE', 'QTY', 'VAT', 'VER'][int('0' + m.group(2))]
        if value is None:
            return u''
        else:
            return super(ValueHiddenInput, self).render(name, value, attrs)


PAYU_DATE_FORMATS = (
    '%Y-%m-%d %H:%M:%S'
)

PAYU_CURRENCIES = (
    ('USD', 'USD'),
    ('RON', 'RON'),
    ('EUR', 'EUR'),
    ('RUB', 'RUB'),
)

PAYU_PAYMENT_METHODS = (
    ('CCVISAMC', 'VISA/Mastercard Card'),
    ('CCAMEX', 'AMEX Card'),
    ('CCDINERS', 'Diners Club Card'),
    ('CCJCB', 'JCB Card'),
    ('WIRE', 'Bank Wire'),
    ('PAYPAL', 'PayPal')
)

PAYU_LANGUAGES = (
    ('RO', u'Română'),
    ('EN', u'English'),
    ('DE', u'Deutsch'),
    ('ES', u'Español'),
    ('FR', u'Français'),
    ('IT', u'Italiano'),
    ('RU', u'Русский'),
)


class OrderWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        all_widgets = (
            ValueHiddenInput(), #PNAME
            ValueHiddenInput(), #PGROUP
            ValueHiddenInput(), #PCODE
            ValueHiddenInput(), #PINFO
            ValueHiddenInput(), #PRICE
            ValueHiddenInput(), #PRICE_TYPE
            ValueHiddenInput(), #QTY
            ValueHiddenInput(), #VAT
            ValueHiddenInput(), #VER
        )
        super(OrderWidget, self).__init__(all_widgets, *args, **kwargs)

    def decompress(self, value):
        return [
            value.get('PNAME', ''), value.get('PGROUP', ''), value.get('PCODE', ''), value.get('PINFO', ''),
            value.get('PRICE', ''), value.get('PRICE_TYPE', ''), value.get('QTY', ''), value.get('VAT', ''),
            value.get('VER', '')
        ]


class OrderField(forms.MultiValueField):
    widget = OrderWidget

    def __init__(self, *args, **kwargs):
        all_fields = (
            forms.CharField(), #PNAME
            forms.CharField(), #PGROUP
            forms.CharField(), #PCODE
            forms.CharField(), #PINFO
            forms.CharField(), #PRICE
            forms.CharField(), #PRICE_TYPE
            forms.CharField(), #QTY
            forms.CharField(), #VAT
            forms.CharField(), #VER
        )
        super(OrderField, self).__init__(all_fields, *args, **kwargs)


class OrdersWidget(forms.MultiWidget):
    is_hidden = True

    def __init__(self, count, *args, **kwargs):
        all_widgets = ((OrderWidget()) for x in range(0, count))
        super(OrdersWidget, self).__init__(all_widgets, *args, **kwargs)


class OrdersField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        products = kwargs.get('initial')
        kwargs['label'] = ''
        all_fields = ()
        if products is not None:
            self.widget = OrdersWidget(len(products))
            all_fields = ((OrderField()) for p in products)
        super(OrdersField, self).__init__(all_fields, *args, **kwargs)


def auto_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class PayULiveUpdateForm(forms.Form):
    MERCHANT = forms.CharField(widget=ValueHiddenInput, initial=MERCHANT)
    ORDER_REF = forms.CharField(widget=ValueHiddenInput, initial='')
    ORDER_DATE = forms.CharField(widget=ValueHiddenInput, initial=auto_now())

    ORDER = OrdersField()
    ORDER_SHIPPING = forms.CharField(widget=ValueHiddenInput)
    PRICES_CURRENCY = forms.ChoiceField(widget=ValueHiddenInput, choices=PAYU_CURRENCIES, initial=CURRENCY)
    DISCOUNT = forms.CharField(widget=ValueHiddenInput)

    PAY_METHOD = forms.ChoiceField(widget=ValueHiddenInput, choices=PAYU_PAYMENT_METHODS)

    ORDER_HASH = forms.CharField(widget=ValueHiddenInput, initial='')

    BILL_FNAME = forms.CharField(widget=ValueHiddenInput)
    BILL_LNAME = forms.CharField(widget=ValueHiddenInput)
    BILL_COUNTRYCODE = forms.CharField(widget=ValueHiddenInput)
    BILL_CITY = forms.CharField(widget=ValueHiddenInput)
    BILL_PHONE = forms.CharField(widget=ValueHiddenInput)
    BILL_EMAIL = forms.CharField(widget=ValueHiddenInput)
    BILL_COMPANY = forms.CharField(widget=ValueHiddenInput)
    BILL_FISCALCODE = forms.CharField(widget=ValueHiddenInput)

    CURRENCY = forms.ChoiceField(widget=ValueHiddenInput, choices=PAYU_CURRENCIES, initial=CURRENCY)
    AUTOMODE = forms.CharField(widget=ValueHiddenInput, initial='1')
    LANGUAGE = forms.ChoiceField(widget=ValueHiddenInput, choices=PAYU_LANGUAGES, initial=LANGUAGE)
    BACK_REF = forms.CharField(widget=ValueHiddenInput, initial=BACK_REF)
    TESTORDER = forms.CharField(widget=ValueHiddenInput, initial=('%s' % TEST).upper())

    def calc_hash(self):
        s = u''
        # We need this hack since payU is not consistent with the order of fields in hash string
        append = u''
        for bf in self:
            if bf.name == 'ORDER_HASH':
                break
            v = bf.value()
            if bf.name == 'ORDER':
                for k in ['PNAME', 'PGROUP', 'PCODE', 'PINFO', 'PRICE', 'PRICE_TYPE', 'QTY', 'VAT', 'VER']:
                    missing = ''
                    for o in v:
                        _v = o.get(k, None)
                        if _v is None:
                            _v = ''
                        missing += r'%s' % _v
                    missing = len(missing) == 0
                    if not missing:
                        for o in v:
                            val = o.get(k, '')
                            itm = u'%d%s' % (len(r'%s' % val), val)
                            if k == 'PRICE_TYPE':
                                append += itm
                            else:
                                s += itm
            else:
                if v is not None:
                    s += u'%d%s' % (len(r'%s' % v), v)
        s += append
        return hmac.new(MERCHANT_KEY, s).hexdigest()

    def __init__(self, **kwargs):
        initial = kwargs.get('initial', {})
        orders = initial.get('ORDER', [])
        for k in ['PNAME', 'PGROUP', 'PCODE', 'PINFO', 'PRICE', 'PRICE_TYPE', 'QTY', 'VAT', 'VER']:
            missing = ''
            for o in orders:
                missing += r'%s' % o.get(k, '')
            missing = len(missing) == 0
            if missing:
                for o in orders:
                    o[k] = None
                    if k == 'QTY': o[k] = 1
                    if k == 'VAT': o[k] = 24

        super(PayULiveUpdateForm, self).__init__(**kwargs)
        self.fields['ORDER'] = OrdersField(initial=orders)
        self.fields['ORDER_HASH'].initial = self.calc_hash()


class PayUIPNForm(forms.ModelForm):
    class Meta:
        model = PayUIPN