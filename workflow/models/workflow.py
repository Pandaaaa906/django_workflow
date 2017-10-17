# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from workflow.models.base_model import BaseModel


class WorkFlow(BaseModel):
    name = models.TextField()
    in_use = models.BooleanField(default=False)
    process_obj = models.ForeignKey(ContentType)


# TODO flow direction: forword, backward
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
    node_type = models.CharField(max_length=100)


class WorkFlowTransition(BaseModel):
    workflow = models.ForeignKey(WorkFlow)
    ancestor_node = models.ForeignKey(WorkFlowNode, blank=True, null=True)
    descendant_node = models.ForeignKey(WorkFlowNode, blank=True, null=True)
    transition_type