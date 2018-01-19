# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.db import models
from workflow.models.workflow import WorkFlow, WorkFlowNode
from workflow.models.base_model import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver


class BaseProcess(BaseModel):
    @property
    def active_workflow(self):
        return WorkFlow.objects.get(in_use=True,
                                    process_obj=self._meta.model,
                                    )

    class Meta:
        abstract = True


class BaseVoucher(BaseModel):

    class Meta:
        abstract = True

    @property
    def get_proceeding(self):
        return Proceeding.objects.get(voucher_type=self._meta.model,
                                      voucher_id=self.id
                                      )


class Voucher(BaseVoucher):

    def submit(self):
        """提交"""
        pass

    class Meta:
        abstract = True


class Proceeding(BaseModel):
    voucher_type = models.ForeignKey(ContentType)
    voucher_obj_id = models.PositiveIntegerField()
    workflow_node = models.ForeignKey(WorkFlowNode, blank=True, null=True, default=None)




# deprecated??
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
        pass

    def retract(self):
        """撤销提交"""
        pass


class ProcessLog(BaseModel):
    work_flow = models.ForeignKey(WorkFlow)
    node = models.ForeignKey(WorkFlowNode)
