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
    # TODO 单据号自动根据code_name得到
    verbose_name = None
    name = None
    code_name = None

    # TODO Limit choices to?
    proceeding = GenericRelation(Proceeding, object_id_field="voucher_obj_id", content_type_field="voucher_type")

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.proceeding is not None:
            raise ValueError("Content of proceeding voucher, can't not modify")
        super(Voucher, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                  update_fields=update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.proceeding is not None:
            raise ValueError("Content of proceeding voucher, can't not modify")
        super(Voucher, self).delete(using=using, keep_parents=keep_parents)

    def submit(self):
        """提交"""
        # 没保存不能提交，报错
        if not self.pk:
            # TODO 要改成合适的错误代码
            raise WorkflowException(error_code=ErrorCode.NO_AVAILABLE_INITIAL_STATE)
        # 如果单据已经提交，报错
        # TODO 审核不通过后
        if self.proceeding:
            # TODO 要改成合适的错误代码
            raise WorkflowException(error_code=ErrorCode.INVALID_NEXT_STATE_FOR_USER)
        Proceeding.objects.get_or_create(voucher_obj=self)
        return True

    def can_submit(self):
        if not self.proceeding:
            return True
        elif Proceeding.objects.filter(voucher_obj=self, )

    def save_submit(self):
        self.save()
        self.submit()

    @property
    def workflow(self):
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

    # TODO 要做成不通过，要另外填单的模型？
    def proceed(self, user, direction=TransactionType.FORWARD):
        """进行单据"""
        self.can_proceed(user)
        self.workflow_node = self.next_pending_node(direction)
        self.current_user = self.workflow_node.user
        self.save()

    def next_node(self, direction=None):
        if direction == TransactionType.FORWARD:
            return self.workflow_node.forward_node
        elif direction == TransactionType.BACKWARD:
            return self.workflow_node.backward_node

    def next_pending_node(self, direction):
        next_node = self.next_node(direction)
        while next_node.node_type == WorkFlowNode.SYS_TYPE:
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
            self.workflow = self.voucher_obj.workflow
            self.workflow_node = WorkFlowNode.objects.get(workflow=self.workflow,
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
