# coding=utf-8
from annoying.fields import JSONField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


from workflow.models.mixin import ModifiedByMixin, CreatedByMixin, ModifiedMixin, CreatedMixin


class Flow(CreatedMixin,
           ModifiedMixin,
           CreatedByMixin,
           ModifiedByMixin,
           models.Model):
    name = models.TextField()
    in_use = models.BooleanField(default=False)
    process_obj = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    copy_to = models.ManyToManyField(User, verbose_name=_("抄送"))

    class Meta:
        unique_together = (
            ("process_obj", "in_use"),
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Flow, self).save(*args, **kwargs)
            FlowNode.objects.create(flow=self, name=_("开始"), node_type=FlowNode.START_TYPE)
            FlowNode.objects.create(flow=self, name=_("结束"), node_type=FlowNode.END_TYPE)
        elif Proceeding.objects.filter(flow=type(self)):
            raise ValueError(_("有正在进行的流程，不能修改"))
        super(Flow, self).save(*args, **kwargs)


class TransactionType:
    FORWARD = 0
    BACKWARD = 2


# TODO flow direction: forward, backward
class FlowNode(CreatedMixin,
               ModifiedMixin,
               CreatedByMixin,
               ModifiedByMixin,
               models.Model):
    START_TYPE = "START"
    END_TYPE = "END"
    USER_TYPE = "USER"
    SYS_TYPE = "SYS"
    NODE_TYPE = (
        (START_TYPE, _("开始")),
        (END_TYPE, _("结束")),
        (USER_TYPE, _("用户节点")),
        (SYS_TYPE, _("系统节点")),
    )
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, db_column='flow_id')
    name = models.TextField(null=True)
    prompt = models.TextField(null=True, blank=True)
    node_type = models.CharField(max_length=100, choices=NODE_TYPE)

    # 负责审核对象：工作组，用户
    q_group_user = Q(app_label='auth')&(Q(model="user")|Q(model="group"))
    approval_group_type = models.ForeignKey(ContentType,
                                            limit_choices_to=q_group_user,
                                            on_delete=models.CASCADE,
                                            null=True)
    approval_group_id = models.PositiveIntegerField(null=True)
    approval_group = GenericForeignKey('approval_group_type', 'approval_group_id')

    forward_node = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name="backword")
    backward_node = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name="forward")

    # 一个系统节点只判断一个条件
    '''
    forward_condition = {'attr': 'fk1__fk2__fk3__attr1',
                        'type': 'int',
                        'value': 500,
                        'operator': 'lt',  # lt, le, gt, ge, eq, ne
                        }
    '''
    forward_condition = JSONField(null=True, blank=True,
                                  default={'attr': None, 'type': None, 'value': None, 'operator': None})

    class Meta:
        unique_together = (
            ('flow', 'name'),
        )



