from celery import shared_task

from workflow.models import Proceeding, FlowNode
from django.utils.translation import ugettext_lazy as _
import operator
# 'lt',  # lt, le, gt, ge, eq, ne


def get_operator(opt):
    return getattr(operator, opt)


@shared_task
def run_proceeding(proceeding_id):
    proceeding = Proceeding.objects.get(id=proceeding_id)
    if proceeding.node.node_type != FlowNode.SYS_TYPE:
        raise ValueError(_("节点状态不是系统节点"))
    voucher_type = proceeding.voucher_type.model_class()
    voucher_id = proceeding.voucher_obj_id
    j_condition = proceeding.node.condition

    field = j_condition.get('field')
    opt = j_condition.get('opt')
    value = j_condition.get('value')

    result = voucher_type.objects.filter(pk=voucher_id).values(field)
    if not result:
        # TODO to ERROR_STATE
        raise ValueError(_("没找到单据？"))
    result = result[0].get(field)
    if get_operator(opt)(result, value):
        # TODO to positive node
        return True
    else:
        # TODO to negative node
        return False


