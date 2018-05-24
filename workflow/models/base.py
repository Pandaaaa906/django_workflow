from itertools import chain

from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _

from workflow.contrib.permissions import VOUCHER_PERMISSIONS



class VoucherBase(ModelBase):
    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__
        if 'post_approval' not in attrs:
            raise ValueError(_("单据没定义post_approval函数"))
        parents = [b for b in bases if isinstance(b, VoucherBase)]
        if not parents:
            return super_new(mcs, name, bases, attrs)

        mod = attrs.get('__module__')
        attr_meta = attrs.setdefault('Meta', type('Meta', (), {}))
        abstract = getattr(attr_meta, 'abstract', False)

        app_config = apps.get_containing_app_config(mod)
        app_label = None
        if getattr(attr_meta, 'app_label', None) is None:
            if app_config is None:
                if not abstract:
                    raise RuntimeError(
                        "Model class %s.%s doesn't declare an explicit "
                        "app_label and isn't in an application in "
                        "INSTALLED_APPS." % (module, name)
                    )
            else:
                app_label = app_config.label

        if not abstract:
            d = {"app_label": app_label,
                 "verbose_name": getattr(attr_meta, "verbose_name", name),
                 "class": name.lower()}

            origin_permissions = getattr(attr_meta, "permissions", ())
            translated_perms = ()
            for codename, p_name in VOUCHER_PERMISSIONS:
                translated_perms += ((codename % d, p_name % d),)
            setattr(attr_meta, "permissions", tuple(chain(origin_permissions, translated_perms)))

        branches = attrs.setdefault("branches", [])
        for branch in branches:
            assert issubclass(branch, models.Model)
            model_name = branch._meta.model_name
            attrs[model_name] = GenericRelation(branch,
                                                object_id_field="source_id",
                                                content_type_field="source_type",
                                                related_query_name=name.lower())

            source_type = models.ForeignKey(ContentType, default=None, null=True, blank=True, on_delete=models.CASCADE)
            source_id = models.PositiveIntegerField(default=None, null=True, blank=True)
            source_obj = GenericForeignKey(ct_field="source_type", fk_field="source_id")

            source_type.contribute_to_class(branch, name="source_type")
            source_id.contribute_to_class(branch, name="source_id")
            source_obj.contribute_to_class(branch, name="source_obj")

        new_class = super_new(mcs, name, bases, attrs)

        if not abstract:
            if getattr(new_class, 'code_name') is None:
                raise ValueError(_("单据code_name不能为空"))
        return new_class


class VoucherInlineBase(ModelBase):
    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__
        if 'parent_voucher' not in attrs:
            raise ValueError(_("没指定父级单据"))
        parents = [b for b in bases if isinstance(b, VoucherInlineBase)]
        if not parents:
            return super_new(mcs, name, bases, attrs)

        model = attrs.pop('parent_voucher')
        mod = __import__('workflow.models', globals(), locals())

        if not issubclass(model, mod.models.Voucher):
            raise ValueError(_("错误的父级单据类型"))

        attrs["parent_voucher"] = models.ForeignKey(model,
                                                    verbose_name=_("单据"),
                                                    on_delete=models.CASCADE,
                                                    related_name="inlines")
        attr_meta = attrs.setdefault('Meta', type('Meta', (), {}))
        branches = attrs.setdefault("branches", [])
        for branch in branches:
            assert issubclass(branch, models.Model)
            model_name = branch._meta.model_name
            attrs[model_name] = GenericRelation(branch,
                                                object_id_field="source_id",
                                                content_type_field="source_type",
                                                related_query_name=name.lower())

            source_type = models.ForeignKey(ContentType, default=None, null=True, blank=True, on_delete=models.CASCADE, editable=False)
            source_id = models.PositiveIntegerField(default=None, null=True, blank=True, editable=False)
            source_obj = GenericForeignKey(ct_field="source_type", fk_field="source_id")

            source_type.contribute_to_class(branch, name="source_type")
            source_id.contribute_to_class(branch, name="source_id")
            source_obj.contribute_to_class(branch, name="source_obj")
        new_class = super_new(mcs, name, bases, attrs)
        return new_class


'''
class BranchBase(ModelBase):
    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, VoucherInlineBase)]
        if not parents:
            return super_new(mcs, name, bases, attrs)
        attrs['source_type'] = models.ForeignKey(ContentType, null=True, default=None, blank=True)
        attrs['source_id'] = models.PositiveIntegerField(null=True, default=None, blank=True)
        return super_new(mcs, name, bases, attrs)
'''
