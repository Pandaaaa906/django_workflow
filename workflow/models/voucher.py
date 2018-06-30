from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from workflow.models import CreatedMixin, ModifiedMixin, CreatedByMixin, ModifiedByMixin, Proceeding, GenericForeignKey
from workflow.models.base import VoucherBase, VoucherInlineBase


class Voucher(CreatedMixin,
              ModifiedMixin,
              CreatedByMixin,
              ModifiedByMixin,
              metaclass=VoucherBase
              ):
    class Meta:
        abstract = True

    # auto added if it has connected inlines
    inlines = None
    proceedings = GenericRelation(Proceeding,
                                  verbose_name=_("流程"),
                                  content_type_field="voucher_type",
                                  object_id_field="voucher_obj_id",
                                  limit_choices_to=~Q(status=Proceeding.RETRACTED))

    @property
    def proceeding(self):
        voucher_type = ContentType.objects.get_for_model(self)
        pcdg = Proceeding.objects.filter(voucher_type=voucher_type, voucher_obj_id=self.id).first()
        return pcdg

    def save(self, user=None, *args, **kwargs):
        if self.pk and not self.editable():
            raise ValueError(_("Item can't not delete"))
        super(Voucher, self).save(*args, **kwargs)
        if not self.proceeding:
            Proceeding.objects.create(voucher_obj=self, created_by=user)

    def delete(self, *args, **kwargs):
        if not self.editable():
            raise ValueError(_("单据已提交，不能删除"))
        super(Voucher, self).delete(*args, **kwargs)

    def post_approval(self):
        """通过审核之后需要执行的函数，"""
        return

    def editable(self):
        proceeding = self.proceeding
        if not self.proceeding:
            return True
        return proceeding.node.editable

    # TODO 根据obj返回
    def get_inlines(self, obj):
        print(obj)
        if issubclass(obj, VoucherInline):
            pass
        return None


class VoucherInline(CreatedMixin,
                    ModifiedMixin,
                    CreatedByMixin,
                    ModifiedByMixin,
                    metaclass=VoucherInlineBase):
    parent_voucher = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.parent_voucher.editable():
            raise ValueError(_("所属单据流程进行中不能修改"))
        super(VoucherInline, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if not self.pk and self.parent_voucher.editable():
            raise ValueError(_("所属单据流程进行中不能删除"))


class Branch(models.Model):
    class Meta:
        abstract = True
