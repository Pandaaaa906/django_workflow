# coding=utf-8
from django.db import models
from workflow.models.workflow import WorkFlow, WorkFlowNode
from workflow.models.base_model import BaseModel


class BaseProcess(BaseModel):
    @property
    def active_workflow(self):
        return WorkFlow.objects.get(in_use=True,
                                    process_obj=self._meta.model,
                                    )


class Process(BaseProcess):
    workflow_node = models.ForeignKey(WorkFlowNode, blank=True, null=True, default=None)

    def start(self):
        if self.workflow_node is None:
            self.workflow_node = WorkFlowNode.objects.get(workflow=self.active_workflow,
                                                          node_type=WorkFlowNode.START_TYPE
                                                          )
        else:
            pass

    def proceed(self, user):
        """判断用户权限"""


    def retract(self):
        """撤销提交"""
        pass


class ProcessLog(BaseModel):
    work_flow = models.ForeignKey(WorkFlow)
    node = models.ForeignKey(WorkFlowNode)
