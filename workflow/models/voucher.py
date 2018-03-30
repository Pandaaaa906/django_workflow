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
              models.Model,
              metaclass=VoucherBase
              ):
    class Meta:
        abstract = True

    # TODO 单据号自动根据code_name得到
    code_name = None
    # auto added if it has connected inlines
    inlines = None
    proceedings = GenericRelation(Proceeding,
                                  verbose_name=_("流程"),
                                  content_type_field="voucher_type",
                                  object_id_field="voucher_obj_id",
                                  limit_choices_to=~Q(status=Proceeding.RETRACTED))

    def save(self, *args, **kwargs):
        if self.pk and self.is_immutable():
            raise ValueError("单据已提交，不能修改")
        super(Voucher, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_immutable():
            raise ValueError(_("单据已提交，不能删除"))
        super(Voucher, self).delete(*args, **kwargs)

    def post_approval(self):
        """通过审核之后需要执行的函数，"""
        return

    def submit(self, user=None):
        """提交"""
        # 没保存不能提交，报错
        if not self.pk:
            raise ValueError(_("单据未保存不能提交"))
        # 如果单据已经提交，报错
        if self.is_immutable():
            raise ValueError(_("已提交单据不能提交"))
        Proceeding.objects.create(voucher_obj=self, created_by=user)

    def retract(self, user=None):
        """撤回，将Proceedings.status设为撤销状态，被审核不通过可以撤回"""
        if self.can_retract():
            self.proceedings.update(status=Proceeding.RETRACTED, modified_by=user, node=None)
        else:
            raise ValueError(_("单据不能撤销"))

    # TODO 审核：ShortCut for Proceeding audit
    def audit(self, user, _pass=True):
        proceeding = self.proceedings.filter(Q(status=Proceeding.PROCESSING))[0]

    def save_submit(self, user):
        self.save(user=user)
        self.submit(user=user)

    def is_immutable(self):
        return getattr(self.proceeding, "status", None) in (Proceeding.PROCESSING,
                                                            Proceeding.REJECTED,
                                                            Proceeding.APPROVED,
                                                            Proceeding.CLOSED)

    def can_retract(self):
        """只有PROCESSING,REJECTED,可以撤回"""
        return getattr(self.proceeding, "status", None) in (Proceeding.PROCESSING, Proceeding.REJECTED)

    def is_processing(self):
        return getattr(self.proceeding, "status", None) == Proceeding.PROCESSING

    def is_finished(self):
        return getattr(self.proceeding, "status", None) in (Proceeding.REJECTED, Proceeding.APPROVED, Proceeding.CLOSED)

    def can_submit(self):
        return getattr(self.proceeding, "status", None) in (Proceeding.RETRACTED, None)

    @property
    def proceeding(self):
        try:
            return self.proceedings.latest('created')
        except Proceeding.DoesNotExist:
            return None


class VoucherInline(CreatedMixin,
                    ModifiedMixin,
                    CreatedByMixin,
                    ModifiedByMixin,
                    models.Model,
                    metaclass=VoucherInlineBase):
    parent_voucher = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.parent_voucher.is_immutable():
            raise ValueError(_("所属单据流程进行中不能修改"))
        super(VoucherInline, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.pk and self.parent_voucher.is_immutable():
            raise ValueError(_("所属单据流程进行中不能删除"))


class Branch(models.Model):
    source_type = models.ForeignKey(ContentType, default=None, null=True, blank=True, on_delete=models.CASCADE)
    source_id = models.PositiveIntegerField(default=None, null=True, blank=True)
    source_obj = GenericForeignKey('source_type', 'source_id')

    class Meta:
        abstract = True
