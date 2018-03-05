from django.contrib import admin

# Register your models here.
from test_app.models import Inquiry, MyVoucher
from django.utils.translation import ugettext_lazy as _


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'cat_no', 'name', 'cas', 'quantity_unit', 'unit', 'quantity',
                    'get_proceeding_status', 'get_created_by')
    actions = ('submit', 'retract')
    search_fields = ('cat_no', 'name', 'cas', 'pk', 'proceeding__status', 'created_by__username')

    def save_model(self, request, obj, form, change):
        is_new = False
        if not obj.pk:
            is_new = True
        super().save_model(request, obj, form, change)
        if is_new:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.save()


    def retract(self, request, queryset):
        for obj in queryset:
            obj.retract(user=request.user)

    def submit(self, request, queryset):
        for obj in queryset:
            obj.submit(user=request.user)

    def get_proceeding_status(self, obj):
        l_result = obj.proceeding.filter().order_by('-created')
        result = None
        if l_result:
            result = l_result[0].status
        return result

    def get_created_by(self, obj):
        return getattr(obj.created_by, 'username', None)

    get_created_by.short_description = _('新增人')
    get_proceeding_status.short_description = _('状态')


admin.site.register(MyVoucher)
