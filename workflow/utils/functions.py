from workflow.models.process import Proceeding


def has_workflow_proceeding(flow):
    if Proceeding.objects.filter(flow=flow).exists():
        return True
    else:
        return False
