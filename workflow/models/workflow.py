# coding=utf-8
from annoying.fields import JSONField
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from workflow.models.base_model import BaseModel


class WorkFlow(BaseModel):
    name = models.TextField()
    in_use = models.BooleanField(default=False)
    process_obj = models.ForeignKey(ContentType)

    copy_to = models.ManyToManyField(User, verbose_name=_("抄送"))

    class Meta:
        unique_together = (
            ("process_obj", "in_use"),
        )


class TransactionType:
    FORWARD = 0
    BACKWARD = 2


# TODO flow direction: forward, backward
class WorkFlowNode(BaseModel):
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

    workflow = models.ForeignKey(WorkFlow)
    node_type = models.CharField(max_length=100, choices=NODE_TYPE)

    user = models.ForeignKey(User, null=True, blank=True)
    name = models.TextField(null=True)
    prompt = models.TextField(null=True, blank=True)

    forward_node = models.ForeignKey('self', null=True)
    backward_node = models.ForeignKey('self', null=True)

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
            ('workflow_id', 'name')
        )


class WorkFlowTransition(BaseModel):
    workflow = models.ForeignKey(WorkFlow)
    ancestor_node = models.ForeignKey(WorkFlowNode, blank=True, null=True)
    descendant_node = models.ForeignKey(WorkFlowNode, blank=True, null=True)
    transition_type
