# coding=utf-8
from django.db import models

# Create your models here.
from workflow.models import Voucher


class MyVoucher(Voucher,
                models.Model):
    name = "TestVoucher"
    code_name = "TEST"
    verbose_name = "测试单据"

    to = models.TextField(null=True, blank=True, default=None)
    want_to = models.TextField(null=True, blank=True, default=None)
    before = models.DateField(null=True, blank=True, default=None)
