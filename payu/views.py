# -*- coding: utf-8 -*-

import hmac
import pytz
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import PayUIPNForm
from .conf import MERCHANT_KEY
from .models import PayUIPN


@require_POST
@csrf_exempt
def ipn(request):
    ipn = PayUIPNForm(request.POST)
    ipn_obj = None
    flag = None

    s = ''
    for k in ['SALEDATE', 'PAYMENTDATE', 'COMPLETE_DATE', 'REFNO', 'REFNOEXT', 'ORDERNO', 'ORDERSTATUS', 'PAYMETHOD',
              'PAYMETHOD_CODE', ]:
        if request.POST.has_key(k):
            s += '%s%s' % (len(request.POST.get(k)), request.POST.get(k))

    hash = hmac.new(MERCHANT_KEY, s).hexdigest()
    if request.POST.get('HASH', '') != hash:
        flag = 'Invalid hash %s. Hash string \n%s' % (request.POST.get('HASH', ''), s)
    else:
        if ipn.is_valid():
            try:
                ipn_obj = ipn.save(commit=False) # When commit = False, object is returned without saving to DB.
            except Exception, e:
                flag = "Exception while processing. (%s)" % e
        else:
            flag = "Invalid form. (%s)" % ipn.errors

    if ipn_obj is None:
        ipn_obj = PayUIPN()

    ipn_obj.initialize(request) # Set query params and sender's IP address

    if flag is not None:
        ipn_obj.set_flag(flag) # We save errors in the flag field

    ipn_obj.save()
    ipn_obj.send_signals()

    date = datetime.now(pytz.UTC).strftime('%Y%m%d%H%M%S')
    hash = hmac.new(MERCHANT_KEY, '00014%s' % date).hexdigest()
    return HttpResponse('<EPAYMENT>%s|%s</EPAYMENT>' % (date, hash))
