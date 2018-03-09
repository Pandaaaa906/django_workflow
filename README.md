#### 🚧Project Under Construction🚧

# Django Workflow

This is a workflow project can be use in building an ERP using django.

To define some vouchers, like Inquiry and Quotation in the example_app:
```python
from django.db import models
from workflow import Voucher, VoucherInline, Branch

# If some model which could be another voucher have source item
class Quotation(Voucher, Branch):
    some = models.TextField()
    log = models.TextField()

    def post_approval(self):
        maybe_create_another_voucher()


class Inquiry(Voucher):
    some = models.TextField()
    information = models.TextField()
    we = models.TextField()
    need = models.TextField()

    # Mostly, after a voucher approved, some new records will be created and connected by the inlines.
    def post_approval(self):
        for obj in self.inlines:
            Quotation.objects.create(source_obj=obj)


# If a Voucher have inlines, define an inline model like this:
class InquiryInline(VoucherInline):
    parent_voucher = Inquiry

    details = models.TextField()

```
