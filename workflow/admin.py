from annoying.fields import JSONField
from django.contrib import admin

# Register your models here.
from django.db import models
from django.forms import TextInput, Textarea
from guardian.admin import GuardedModelAdmin

from workflow.models import Flow, Node, Proceeding, Transaction, FlowVoucher
from django.utils.translation import ugettext_lazy as _


@admin.register(Proceeding)
class ProceedingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'get_voucher_id', 'get_flow_name', 'get_node_name')

    def get_voucher_id(self, obj):
        return obj.voucher_obj.code_name

    def get_flow_name(self, obj):
        return getattr(obj.flow, 'name', None)

    def get_node_name(self, obj):
        return getattr(obj.node, 'name', None)

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/4.2.1/jsoneditor.js",)


class JSONWidget(Textarea):
    pass


class BaseInline(admin.TabularInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
        JSONField: {'widget': Textarea(attrs={'rows': 3, 'cols': 20})}
    }


class NodeInline(BaseInline):
    model = Node
    extra = 0


class TransactionInline(BaseInline):
    model = Transaction
    extra = 0


class VoucherInline(admin.TabularInline):
    model = FlowVoucher
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
        JSONField: {'widget': Textarea(attrs={'rows': 3, 'cols': 20})}
    }


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'created', 'created_by', 'get_len_nodes', 'get_vouchers')
    inlines = [VoucherInline, NodeInline, TransactionInline]
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 30})},
    }
    fieldsets = (
        [None, {
            'fields': ('name',),
        }],

    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    def get_len_nodes(self, obj):
        return Node.objects.filter(flow=obj).count()

    get_len_nodes.short_description = _("节点数量")

    def get_vouchers(self, obj):
        results = FlowVoucher.objects.filter(flow=obj)
        return "<br>".join((str(result) for result in results))

    get_vouchers.short_description = _("单据列表")
    get_vouchers.allow_tags = True


admin.site.register(FlowVoucher)


class AuthorAdmin(GuardedModelAdmin):
    pass


admin.site.register(Transaction, AuthorAdmin)
