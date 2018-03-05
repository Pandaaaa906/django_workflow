from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from workflow.models import CreatedMixin, ModifiedMixin, CreatedByMixin, ModifiedByMixin, Proceeding
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

    proceeding = GenericRelation(Proceeding,
                                 verbose_name=_("流程"),
                                 content_type_field="voucher_type",
                                 object_id_field="voucher_obj_id",
                                 limit_choices_to=~Q(status=Proceeding.RETRACTED))

    def has_unretracted_process(self):
        if self.proceeding.filter(~Q(status=Proceeding.RETRACTED)).exists():
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        if self.pk and self.has_unretracted_process():
            raise ValueError("单据已提交，不能修改")
        super(Voucher, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.has_unretracted_process():
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
        # TODO 审核不通过后
        if self.has_unretracted_process():
            raise ValueError(_("已提交单据不能提交"))
        Proceeding.objects.create(voucher_obj=self, created_by=user)

    def can_retract(self):
        """只有PROCESSING,REJECTED,可以撤回"""
        if self.proceeding.filter(Q(status=Proceeding.PROCESSING) | Q(status=Proceeding.REJECTED)).exists():
            return True
        else:
            return False

    def retract(self, user=None):
        """撤回，将Proceedings.status设为撤销状态，被审核不通过可以撤回"""
        if self.can_retract():
            self.proceeding.update(status=Proceeding.RETRACTED, modified_by=user)
        else:
            raise ValueError(_("单据没有进入流程，不能撤销"))

    # TODO 审核：ShortCut for Proceeding audit
    def audit(self, user, _pass=True):
        proceeding = self.proceeding.filter(Q(status=Proceeding.PROCESSING))[0]

    def get_processing_proceed(self):
        return self.proceeding.filter(Q(status=Proceeding.PROCESSING))[0]

    def save_submit(self, user):
        self.save(user=user)
        self.submit(user=user)


class VoucherInline(CreatedMixin,
                    ModifiedMixin,
                    CreatedByMixin,
                    ModifiedByMixin,
                    models.Model,
                    metaclass=VoucherInlineBase):
    parent_voucher = None

    class Meta:
        abstract = True
