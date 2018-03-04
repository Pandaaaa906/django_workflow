from itertools import chain

from django.apps import apps
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

        new_class = super_new(mcs, name, bases, attrs)

        if not abstract:
            meta = new_class._meta
            if getattr(new_class, 'verbose_name') is None:
                raise ValueError(_("单据名称不能为空"))
            if getattr(new_class, 'code_name') is None:
                raise ValueError(_("单据code_name不能为空"))
            setattr(meta, 'verbose_name', new_class.verbose_name)
        return new_class