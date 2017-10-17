# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.db import models
from base_model import BaseModel


class WorkFlow(BaseModel):
    name = models.TextField()
    in_use = models.BooleanField(default=False)
    process_obj = models.ForeignKey(ContentType)

    def start(self, process_instance):
        pass


# TODO flow direction: forword, backward
class WorkFlowNode(BaseModel):
    START_TYPE = "START"
    END_TYPE = "END"
    NODE_TYPE = (
        (START_TYPE, "开始"),
        (END_TYPE, "结束"),
    )
    workflow = models.ForeignKey(WorkFlow)
    ancestor_node = models.ForeignKey('self', blank=True, null=True)
    descendant_node = models.ForeignKey('self', blank=True, null=True)

    node_type = models.CharField(max_length=100)