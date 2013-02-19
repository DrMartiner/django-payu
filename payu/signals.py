# -*- coding: utf-8 -*-

from django.dispatch import Signal

payment_completed = Signal() # Sent when a payment is completed.

payment_authorized = Signal() # Sent when a payment is authorized (PAYMENT_AUTHORIZED or PAYMENT_RECEIVED)

payment_flagged = Signal()