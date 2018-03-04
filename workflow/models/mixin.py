# coding=utf-8
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    created = models.DateTimeField(verbose_name=_("新增时间"), auto_now_add=True, null=True, blank=True, editable=False)

    class Meta:
        abstract = True


class ModifiedMixin(models.Model):
    modified = models.DateTimeField(verbose_name=_("修改时间"), auto_now=True, null=True, blank=True, editable=False)

    class Meta:
        abstract = True


class CreatedByMixin(models.Model):
    created_by = models.ForeignKey(User, verbose_name=_("新建人"),
                                   null=True, blank=True, default=None,
                                   editable=False,
                                   on_delete="CASCADE",
                                   related_name="%(app_label)s_%(class)s_created")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_by = kwargs.pop('user', None)
        super(CreatedByMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class ModifiedByMixin(models.Model):
    modified_by = models.ForeignKey(User, verbose_name=_("修改人"),
                                    null=True, blank=True, default=None,
                                    editable=False,
                                    on_delete="CASCADE",
                                    related_name="%(app_label)s_%(class)s_modified")

    def save(self, *args, **kwargs):
        self.modified_by = kwargs.pop('user', None)
        super(ModifiedByMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class PreviousVoucherMixin(models.Model):
    upper_voucher_type = models.ForeignKey(ContentType, null=True, on_delete="CASCADE")
    upper_voucher_id = models.PositiveIntegerField(null=True)
    upper_voucher = GenericForeignKey('upper_voucher_type', 'upper_voucher_id')

    class Meta:
        abstract = True



