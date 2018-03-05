# coding=utf-8
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from .flow import Flow, FlowNode
from workflow.models.mixin import ModifiedByMixin, CreatedByMixin, ModifiedMixin, CreatedMixin
from workflow.contrib.error_code import ErrorCode
from workflow.contrib.exceptions import WorkflowException


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

    voucher_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    voucher_obj_id = models.PositiveIntegerField()
    voucher_obj = GenericForeignKey('voucher_type', 'voucher_obj_id')

    flow = models.ForeignKey(Flow, on_delete=models.CASCADE)
    node = models.ForeignKey(FlowNode, on_delete=models.CASCADE, null=True)

    # TODO 完善audit
    def audit(self, user, _pass=True):
        """
        检查节点Type,
        是否用户节点，
        if _pass == True，
            设self.workflow_node = self.workflow_node.next_node
        else:
            self.reject(user)

        """
        pass

    def robot(self):
        """
        处理系统节点，

        if proceeding_instance.node.node_type is not SYSTEM:
            return
        for condition in conditions:
            if condition:

        :return:
        """

    def hand_over(self, user, to_user):
        self.can_proceed(user)
        self.current_user = to_user
        self.save()

    # TODO 检查self.
    def can_proceed(self, user):
        if self.current_user != user:
            raise WorkflowException(error_code=ErrorCode.INVALID_NEXT_STATE_FOR_USER)
        return True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.flow = self.get_active_workflow()
            self.node = FlowNode.objects.get(flow=self.flow,
                                             node_type=FlowNode.START_TYPE)
        super(Proceeding, self).save(*args, **kwargs)
        # TODO 如果是系统节点，新建个机器人任务处理
        if self.node.node_type == FlowNode.END_TYPE:
            self.voucher_obj.post_approval()
            self.status = self.APPROVED

    class Meta:
        unique_together = (
            # ("voucher_type", "voucher_obj_id"),
        )


class ProcessLog(CreatedMixin,
                 ModifiedMixin,
                 CreatedByMixin,
                 ModifiedByMixin):
    proceeding = models.ForeignKey(Proceeding, on_delete=models.CASCADE)


# TODO 每当Proceeding变化，添加ProecessLog
@receiver(post_save)
def proceeding_log(sender, *args, **kwargs):
    pass
