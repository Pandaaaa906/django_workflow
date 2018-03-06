# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.
from workflow.models import Voucher, VoucherInline, Branch


class MyVoucher(Voucher):
    code_name = "TEST"

    to = models.TextField(null=True, blank=True, default=None)
    want_to = models.TextField(null=True, blank=True, default=None)
    before = models.DateField(null=True, blank=True, default=None)

    class Meta:
        verbose_name = _("测试单据")

    def post_approval(self):
        pass


class Quotation(Voucher, Branch):
    code_name = "QO"
    product_cat_no = models.TextField()

    def post_approval(self):
        pass


class Inquiry(Voucher):
    code_name = "IO"

    customer = models.TextField(verbose_name=_("客户"), null=True, default=None, blank=True)
    sales = models.ForeignKey(User,
                              verbose_name=_("销售"),
                              on_delete=models.CASCADE,
                              null=True, default=None, blank=True)

    class Meta:
        verbose_name = _("询单")

    def post_approval(self):
        for obj in self.inlines.all():
            Quotation.objects.create(source_obj=obj)


class InquiryInline(VoucherInline):
    parent_voucher = Inquiry

    UNIT_MG = "mg"
    UNIT_KG = "kg"
    UNIT_G = "g"
    UNIT_ML = "ml"
    UTIT_UL = "ul"
    UNIT_L = 'L'

    UNIT_CHOICES = {
        (UNIT_MG, "mg"),
        (UNIT_KG, "kg"),
        (UNIT_G, "g"),
        (UNIT_ML, "ml"),
        (UTIT_UL, "ul"),
        (UNIT_L, 'L'),
    }

    cat_no = models.TextField(_("货号"), null=True, blank=True, default=None)
    cas = models.TextField(_("cas"), null=True, blank=True, default=None)
    name = models.TextField(_("名称"), null=True, blank=True, default=None)
    quantity_unit = models.FloatField(_("单位数量"), null=True, blank=True, default=None)
    unit = models.TextField(_("单位"), choices=UNIT_CHOICES, null=True, blank=True, default=UNIT_MG)
    quantity = models.PositiveIntegerField(_("数量"), default=1, blank=True)

    class Meta:
        verbose_name = _("询单内联")
