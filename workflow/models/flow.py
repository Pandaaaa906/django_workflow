# coding=utf-8
from annoying.fields import JSONField
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from workflow.models.mixin import ModifiedByMixin, CreatedByMixin, ModifiedMixin, CreatedMixin


class Flow(CreatedMixin,
           ModifiedMixin,
           CreatedByMixin,
           ModifiedByMixin,
           models.Model):
    name = models.TextField()

    class Meta:
        pass

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        mod = __import__('workflow.models', globals(), locals())
        Proceeding = mod.models.Proceeding
        if not self.pk:
            super(Flow, self).save(*args, **kwargs)
            Node.objects.create(flow=self, name=_("initial"), editable=True, is_start=True)
        elif Proceeding.objects.filter(flow=self, node__editable=False):
            raise ValueError(_("Proceeding current workflow, can not edit"))
        super(Flow, self).save(*args, **kwargs)


class FlowVoucher(models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.PROTECT)
    voucher_type = models.OneToOneField(ContentType, on_delete=models.PROTECT)

    def __str__(self):
        return " | ".join((self.voucher_type.app_label, self.voucher_type.model)) + " >> " + str(self.flow)

    class Meta:
        pass


class CustomJSONField(JSONField):
    def get_prep_value(self, value):
        if isinstance(value, str):
            try:
                value = self.deserializer(value)
                return super().get_prep_value(value)
            except:
                return super().get_prep_value(value)


class Node(CreatedMixin,
           ModifiedMixin,
           CreatedByMixin,
           ModifiedByMixin,
           models.Model
           ):
    flow = models.ForeignKey(Flow, on_delete=models.PROTECT, db_column='flow_id')
    name = models.TextField(null=True)
    prompt = models.TextField(null=True, blank=True)

    editable = models.BooleanField(default=True)
    is_start = models.BooleanField(default=False)
    is_end = models.BooleanField(default=False)

    def __str__(self):
        return "/".join((self.flow.name, self.name))

    class Meta:
        unique_together = (
            ('flow', 'name'),
            ('flow', 'is_start'),
        )
        ordering = ['flow', 'id']


class Transaction(CreatedMixin,
                  ModifiedMixin,
                  CreatedByMixin,
                  ModifiedByMixin,
                  models.Model
                  ):
    flow = models.ForeignKey(Flow, on_delete=models.PROTECT, db_column='flow_id')
    name = models.TextField(null=True)
    prompt = models.TextField(null=True, blank=True)

    previous_node = models.ForeignKey(Node,
                                      on_delete=models.PROTECT,
                                      related_name="next_transactions"
                                      )

    next_node = models.ForeignKey(Node,
                                  on_delete=models.PROTECT,
                                  related_name="previous_transactions"
                                  )

    USER_TYPE = "USER"
    SYS_TYPE = "SYS"
    NODE_TYPE = (
        (USER_TYPE, _("User Transaction")),
        (SYS_TYPE, _("System Transaction")),
    )

    transaction_type = models.CharField(max_length=100, choices=NODE_TYPE, default=USER_TYPE)

    # 一个系统节点只判断一个条件
    DEFAULT_CONDITION = {"field": None,  # 'fk1__fk2__fk3__attr1',
                         "type": None,  # 'int',
                         "value": None,  # 500,
                         "operator": None,  # 'lt',  # lt, le, gt, ge, eq, ne
                         "positive_node_id": None,
                         "negative_node_id": None,
                         }

    condition = CustomJSONField(null=True, blank=True,
                                default=DEFAULT_CONDITION)

    class Meta:
        permissions = (
            ('view_transaction', 'View Transaction'),
            ('can_transaction', 'Can Transaction'),
        )
