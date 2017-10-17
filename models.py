# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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


class Process(BaseModel):
    status_id = models.IntegerField(blank=True, null=True)

    def push(self):
        self.active_workflow.start(self)

    def retract(self):
        pass


    @property
    def active_workflow(self):
        return WorkFlow.objects.get(in_use=True,
                                               process_obj=self._meta.model,
                                               )

class ProcessLog(BaseModel):
    work_flow = models.ForeignKey(WorkFlow)
    node = models.ForeignKey(WorkFlowNode)