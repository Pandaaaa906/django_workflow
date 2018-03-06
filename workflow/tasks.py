from celery import shared_task

from workflow.models import Proceeding, FlowNode
from django.utils.translation import ugettext_lazy as _


@shared_task
def run_proceeding(proceeding_id):
    proceeding = Proceeding.objects.get(id=proceeding_id)
    if proceeding.node.node_type != FlowNode.SYS_TYPE:
        raise ValueError(_("节点状态不是系统节点"))

    j_condition = proceeding.node.condition
    fields = j_condition.get()