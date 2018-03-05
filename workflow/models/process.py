# coding=utf-8
from django.contrib.auth.models import User, Group
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

    # TODO 检查self.
    def can_audit_by(self, user):
        # 如果不是USER_TYPE，返回False
        if self.node.node_type != FlowNode.USER_TYPE:
            print("节点类型不是用户类型")
            return False
        app_group = self.node.approval_group_type.model_class()
        app_ins = self.node.approval_group
        if app_group is Group and not user.groups.filter(name=app_ins.name).exists():
            print("节点组里没有该用户")
            return False
        elif app_group is User and app_ins is not user:
            print("节点用户不是该用户")
            return False
        return True

    # TODO 完善audit
    def audit(self, user, _pass=True, comment=None):
        if not self.can_audit_by(user):
            raise ValueError(_("不能审核"))
        if _pass:
            print(user, "审核中")
            self.node = self.node.next_node
        else:
            self.status = self.REJECTED
        self.save(user=user)
        # TODO 新建ProceedingLog

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
        self.can_audit_by(user)
        self.current_user = to_user
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.flow = self.get_active_workflow()
            self.node = FlowNode.objects.get(flow=self.flow,
                                             node_type=FlowNode.START_TYPE).next_node
        if self.node.node_type == FlowNode.END_TYPE:
            self.voucher_obj.post_approval()
            self.status = self.APPROVED
        super(Proceeding, self).save(*args, **kwargs)
        # TODO 如果是系统节点，新建个机器人任务处理


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
