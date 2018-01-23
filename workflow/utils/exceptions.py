
class WorkflowException(Exception):
    code = None

    def __init__(self, error_code, *args, **kwargs):
        super(WorkflowException, self).__init__(*args, **kwargs)
        self.code = error_code
