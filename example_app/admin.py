from django.contrib import admin

# Register your models here.
from django.db import models
from django.forms import TextInput, Textarea

from example_app.models import Inquiry, MyVoucher, InquiryInline, Quotation
from django.utils.translation import ugettext_lazy as _

from workflow.models import Proceeding


class SmallTextArea(object):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 20})},
    }


class FlowNodeInline(SmallTextArea, admin.TabularInline):
    model = InquiryInline
    extra = 0


class VoucherAdmin(SmallTextArea, admin.ModelAdmin):
    actions = ('submit', 'retract', 'audit')
    list_display = ('get_proceeding_status', 'get_created_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    def retract(self, request, queryset):
        for obj in queryset:
            obj.retract(user=request.user)

    def submit(self, request, queryset):
        for obj in queryset:
            obj.submit(user=request.user)

    def audit(self, request, queryset):
        for obj in queryset:
            obj.proceeding.get(status=Proceeding.PROCESSING).audit(user=request.user)

    def get_proceeding_status(self, obj):
        result = getattr(obj.proceeding, "status", None)
        return result

    def get_node_name(self, obj):
        result = getattr(obj.proceeding.node, 'name', None)
        return result

    def get_created_by(self, obj):
        return getattr(obj.created_by, 'username', None)

    get_created_by.short_description = _('新增人')
    get_proceeding_status.short_description = _('状态')


@admin.register(Inquiry)
class InquiryAdmin(VoucherAdmin, admin.ModelAdmin):
    list_display = ('pk', 'get_customer', 'get_sales_name', 'get_proceeding_status', 'get_node_name', 'get_created_by',)

    inlines = [FlowNodeInline, ]
    search_fields = ('cat_no', 'name', 'cas', 'pk', 'proceeding__status', 'created_by__username', 'quotation__product_cat_no')

    fieldsets = (
        [None, {
            'fields': ('customer', 'sales'),
        }],
        ['Node', {
            'classes': ('collapse',),
            'fields': (),
        }]

    )

    def get_sales_name(self, obj):
        return getattr(obj.sales, 'username', None)

    def get_customer(self, obj):
        return obj.customer


@admin.register(MyVoucher)
class MyVoucherAdmin(VoucherAdmin, admin.ModelAdmin):
    list_display = ('pk', 'to', 'want_to', 'before',
                    'get_proceeding_status', 'get_created_by')


@admin.register(Quotation)
class QuotationAdmin(VoucherAdmin):
    list_display = ('pk', 'product_cat_no', 'get_inquiry_cat_no', 'get_proceeding_status')

    def get_inquiry_cat_no(self, obj):
        return obj.source_obj.cat_no
