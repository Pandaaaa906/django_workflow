# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.db import models
from workflow.models.workflow import WorkFlow, WorkFlowNode
from workflow.models.base_model import BaseModel


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
