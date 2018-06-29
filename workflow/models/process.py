# coding=utf-8
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from .flow import Flow, Node, FlowVoucher
from workflow.models.mixin import ModifiedByMixin, CreatedByMixin, ModifiedMixin, CreatedMixin


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
            flow_voucher = FlowVoucher.objects.get(voucher_type=self.voucher_type)
            flow = flow_voucher.flow
        except FlowVoucher.DoesNotExist:
            raise ValueError(_("Corresponding Workflow Does Not Exist"))
        return flow

    voucher_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    voucher_obj_id = models.PositiveIntegerField()
    voucher_obj = GenericForeignKey('voucher_type', 'voucher_obj_id')

    flow = models.ForeignKey(Flow, on_delete=models.PROTECT)
    node = models.ForeignKey(Node, on_delete=models.PROTECT, null=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.pk:
            self.flow = self.get_active_workflow()
            if self.flow is not None:
                self.node = Node.objects.get(flow=self.flow, is_start=True)
        if self.node.is_end:
            self.voucher_obj.post_approval()
            self.status = self.APPROVED
        super(Proceeding, self).save(*args, **kwargs)
        # TODO 如果是系统节点，新建个机器人任务处理

    def delete(self, using=None, keep_parents=False):
        if self.pk:
            raise ValueError(_("Can't delete a proceeding instance "))

    def run_transaction(self, transaction, user=None):
        trx = self.node.next_transactions.filter(name=transaction).first()
        if trx is not None:
            self.node = trx.next_node
            self.save()
            return True
        raise ValueError(_("Not a Authorized Transaction"))

    class Meta:
        unique_together = (
            ("voucher_type", "voucher_obj_id"),
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
