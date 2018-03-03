# coding=utf-8
from django.db import models

# Create your models here.
from workflow.models import Voucher


class MyVoucher(Voucher,
                models.Model):
    code_name = "TEST"
    verbose_name = "测试单据"

    to = models.TextField(null=True, blank=True, default=None)
    want_to = models.TextField(null=True, blank=True, default=None)
    before = models.DateField(null=True, blank=True, default=None)


class Inquiry(Voucher,
              models.Model):
    code_name = "IO"
    verbose_name = "询单"
    cat_no = models.TextField(null=True, blank=True, default=None)
    cas = models.TextField(null=True, blank=True, default=None)
    name = models.TextField(null=True, blank=True, default=None)
    quantity_unit = models.FloatField(null=True, blank=True, default=None)
    unit = models.TextField(null=True, blank=True, default=None)
    quantity = models.PositiveIntegerField(default=1, blank=True)

