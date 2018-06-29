from datetime import datetime, date
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
# Create your views here.
from django.views import View
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from workflow.contrib.functions import get_transactions
from workflow.models import Voucher


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        print(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        return super().default(obj)


# TODO
class ProcessTransaction(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ProcessTransaction, self).dispatch(request, *args, **kwargs)

    def get(self, request, app_label, model_name, obj_pk, transaction=None, *args, **kwargs):
        results = list(get_transactions(app_label, model_name, obj_pk).values())
        return JsonResponse(results, encoder=LazyEncoder, safe=False)

    def post(self, request, app_label, model_name, transaction, obj_pk, *args, **kwargs):

        model = apps.get_model(app_label, model_name)
        if not issubclass(model, Voucher):
            raise ValueError(_("It's not a voucher type"))
        obj = get_object_or_404(model, pk=obj_pk)
        trx = obj.proceeding.run_transaction(transaction, user=request.user)

        return HttpResponse(str(trx))

