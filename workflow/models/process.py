# coding=utf-8
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from workflow.models.base import VoucherBase
from .flow import Flow, FlowNode, TransactionType
from workflow.models.mixin import ModifiedByMixin, CreatedByMixin, ModifiedMixin, CreatedMixin
from workflow.utils.error_code import ErrorCode
from workflow.utils.exceptions import WorkflowException


class Proceeding(CreatedMixin,
                 ModifiedMixin,
                 CreatedByMixin,
                 ModifiedByMixin,
                 models.Model):
    PROCESSING = "PROCESSING"
    CLOSED = "POS_CLOSED"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    RETRACTED = "RETRACTED"

    def get_active_workflow(self):
        try:
            flow = Flow.objects.get(in_use=True,
                                    process_obj=self.voucher_type,
                                    )
        except Flow.DoesNotExist:
            raise ValueError("单据没有对应流程")
        return flow

    STATUS = (
        (PROCESSING, _("进行中")),
        (CLOSED, _("关闭")),
        (REJECTED, _("驳回")),
        (APPROVED, _("通过")),
        (RETRACTED, _("撤回"))
    )
    status = models.CharField(verbose_name=_("状态"), choices=STATUS, default=PROCESSING, max_length=100)

    voucher_type = models.ForeignKey(ContentType, on_delete="CASCADE")
    voucher_obj_id = models.PositiveIntegerField()
    voucher_obj = GenericForeignKey('voucher_type', 'voucher_obj_id')

    flow = models.ForeignKey(Flow, on_delete="CASCADE")
    workflow_node = models.ForeignKey(FlowNode, on_delete="CASCADE")

    def proceed(self, user, direction=TransactionType.FORWARD):
        """进行单据"""
        self.can_proceed(user)
        self.workflow_node = self.next_pending_node(direction)
        self.save()

    def next_node(self, direction=None):
        if direction == TransactionType.FORWARD:
            return self.workflow_node.forward_node
        elif direction == TransactionType.BACKWARD:
            return self.workflow_node.backward_node

    def next_pending_node(self, direction):
        next_node = self.next_node(direction)
        while next_node.node_type == FlowNode.SYS_TYPE:
            # TODO fake code
            if next_node.forward_condition:
                next_node = next_node.forward_node
            else:
                next_node = next_node.backward_node
        return next_node

    def hand_over(self, user, to_user):
        self.can_proceed(user)
        self.current_user = to_user
        self.save()

    def can_proceed(self, user):
        if self.current_user != user:
            raise WorkflowException(error_code=ErrorCode.INVALID_NEXT_STATE_FOR_USER)
        return True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.flow = self.get_active_workflow()
            self.workflow_node = FlowNode.objects.get(flow=self.flow,
                                                      node_type=FlowNode.START_TYPE)
        super(Proceeding, self).save(*args, **kwargs)
        if self.workflow_node.node_type == FlowNode.END_TYPE:
            self.post_approval()

    class Meta:
        unique_together = (
            # ("voucher_type", "voucher_obj_id"),
        )


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
    verbose_name = None
    code_name = None

    proceeding = GenericRelation(Proceeding,
                                 verbose_name=_("流程"),
                                 content_type_field="voucher_type",
                                 object_id_field="voucher_obj_id")

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
        Proceeding.objects.create(voucher_obj=self)

    def retract(self):
        """撤回，将Proceedings.status设为撤销状态，被拒绝可以撤回"""
        if self.proceeding.exists():
            self.proceeding.update(status=Proceeding.RETRACTED)
        else:
            raise ValueError(_("单据没有进入流程，不能撤销"))

    def approve(self, user):
        pass

    def save_submit(self, user):
        self.save(user=user)
        self.submit(user=user)


class ProcessLog(CreatedMixin,
                 ModifiedMixin,
                 CreatedByMixin,
                 ModifiedByMixin):
    proceeding = models.ForeignKey(Proceeding, on_delete="CASCADE")


# TODO 每当Proceeding变化，添加ProecessLog
@receiver(post_save)
def proceeding_log(sender, *args, **kwargs):
    pass
