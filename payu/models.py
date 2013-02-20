# -*- coding: utf-8 -*-

from django.db import models
from payu.signals import payment_completed, payment_authorized, payment_flagged

PAYU_PAYMENT_STATUS = (
    ('PAYMENT_AUTHORIZED', 'PAYMENT_AUTHORIZED'),
    ('PAYMENT_RECEIVED', 'PAYMENT_RECEIVED'),
    ('TEST', 'TEST'),
    ('CASH', 'CASH'),
    ('COMPLETE', 'COMPLETE'),
    ('REVERSED', 'REVERSED'),
    ('REFUND', 'REFUND')
)


class PayUIPN(models.Model):
    HASH = models.CharField(max_length=64)
    SALEDATE = models.DateTimeField('Sale date', blank=True, null=True)
    COMPLETE_DATE = models.DateTimeField('Complete date', blank=True, null=True)
    PAYMENTDATE = models.DateTimeField('Payment date', blank=True, null=True)
    REFNO = models.CharField('ePayment reference', max_length=9)
    REFNOEXT = models.CharField('Merchant reference', max_length=100)
    ORDERNO = models.CharField('Merchant order #', max_length=6)
    ORDERSTATUS = models.CharField('Status', max_length=18, choices=PAYU_PAYMENT_STATUS)
    PAYMETHOD_CODE = models.CharField('Payment method', max_length=10)

    response = models.TextField(blank=True)
    ip_address = models.IPAddressField(blank=True)
    flag = models.BooleanField(default=False)
    flag_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def initialize(self, request):
        self.response = getattr(request, request.method).urlencode()
        self.ip_address = request.META.get('REMOTE_ADDR', '')

    def set_flag(self, info):
        """Sets a flag on the transaction and also sets a reason."""
        self.flag = True
        self.flag_info += info

    def send_signals(self):
        if self.flag:
            payment_flagged.send(sender=self)
            return
        if self.ORDERSTATUS in ['PAYMENT_AUTHORIZED', 'PAYMENT_RECEIVED', 'TEST']:
            payment_authorized.send(sender=self)
        if self.ORDERSTATUS == 'COMPLETE':
            payment_completed.send(sender=self)

    def __unicode__(self):
        return u'<IPN: %s>' % self.REFNO

    class Meta:
        db_table = 'payu_ipn'
        ordering = ('created_at',)
        verbose_name = 'PayU IPN'
        verbose_name_plural = 'PayU IPNs'
