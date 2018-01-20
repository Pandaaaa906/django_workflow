# coding=utf-8
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from workflow.models.workflow import WorkFlow, WorkFlowNode, TransactionType
from workflow.models.base_model import BaseModel
from workflow.utils.error_code import ErrorCode
from workflow.utils.exceptions import WorkflowException


class Voucher(BaseModel):
    name = None
    proceeding = GenericRelation(Proceeding)

    def submit(self):
        """提交"""
        # 没保存不能提交，报错
        if not self.pk:
            # TODO 要改成合适的错误代码
            raise WorkflowException(error_code=ErrorCode.NO_AVAILABLE_INITIAL_STATE)
        # 如果单据已经提交，报错
        pcd, created = Proceeding.objects.get_or_create(voucher_obj=self)
        if not created:
            # TODO 要改成合适的错误代码
            raise WorkflowException(error_code=ErrorCode.INVALID_NEXT_STATE_FOR_USER)

    @property
    def active_workflow(self):
        return WorkFlow.objects.get(in_use=True,
                                    process_obj=self._meta.model,
                                    )

    class Meta:
        abstract = True


class Proceeding(BaseModel):
    voucher_type = models.ForeignKey(ContentType)
    voucher_obj_id = models.PositiveIntegerField()
    voucher_obj = GenericForeignKey('voucher_type', 'voucher_obj_id')

    workflow = models.ForeignKey(WorkFlow)
    workflow_node = models.ForeignKey(WorkFlowNode)

    current_user = models.ForeignKey(User)

    def post_approval(self):
        """通过审核之后需要执行的函数，"""

    # TODO 要做成不通过，要另外填单的模型
    def proceed(self, user, direction=TransactionType.FORWARD):
        """进行单据"""
        self.can_proceed(user)
        if direction == TransactionType.FORWARD:
            self.workflow_node = self.workflow_node.forward_node
        elif direction == TransactionType.BACKWARD:
            self.workflow_node = self.workflow_node.backward_node
        self.current_user = self.workflow_node.user
        self.save()

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
            self.workflow = self.voucher_obj.active_workflow
            self.workflow_node = WorkFlowNode.objects.get(workflow=self.active_workflow,
                                                          node_type=WorkFlowNode.START_TYPE)
        super(Proceeding, self).save(*args, **kwargs)
        if self.workflow_node.node_type == WorkFlowNode.END_TYPE:
            self.post_approval()

    class Meta:
        unique_together = (
            ("voucher_type", "voucher_obj_id"),
        )


class ProcessLog(BaseModel):
    proceeding = models.ForeignKey(Proceeding)


# TODO 每当Proceeding变化，添加ProecessLog
@receiver(post_save)
def proceeding_log(sender, *args, **kwargs):
    pass
