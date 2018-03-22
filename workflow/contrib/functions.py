from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models import ManyToOneRel, ForeignKey, ManyToManyRel
from django.db.models.constants import LOOKUP_SEP


def get_keys_from_model(model, max_depth=1, **kwargs):
    """
    根据输入的模型，递归输出所有包括外键的字段(field_name, field_verbose_name)
    :param model:
    :param max_depth:
    :param kwargs:
    :return:
    """
    _cur_depth = kwargs.pop("cur_depth", 0)
    _name_prefix = kwargs.pop("name_prefix", "")
    verbose_name_prefix = kwargs.pop("verbose_name_prefix", "")
    last_field_name = kwargs.pop("last_field_name", "")
    _s_models = kwargs.pop("s_models", set())
    l_fields = model._meta.get_fields()

    if _cur_depth >= max_depth:
        return

    for field in l_fields:
        if isinstance(field, (ManyToOneRel, ForeignKey, ManyToManyRel, GenericForeignKey, GenericRelation)):
            if isinstance(field, (ManyToOneRel, ManyToManyRel)):
                print('a', field)
                _model = field.field.model
                _field_name = field.field.name
            else:
                print('b', field)
                _model = field.related_model
                _field_name = field.name
            if _model is None:
                continue
            _model_verbose_name = _model._meta.verbose_name.title()
            if _name_prefix:
                name_prefix = LOOKUP_SEP.join((_name_prefix, field.name))
            else:
                name_prefix = field.name
            key = last_field_name + "_" + _field_name + "_" + _model_verbose_name
            if key in _s_models:
                continue
            else:
                _s_models.add(key)
            for i in get_keys_from_model(_model, max_depth,
                                         cur_depth=_cur_depth + 1,
                                         name_prefix=name_prefix,
                                         verbose_name_prefix=verbose_name_prefix + _model_verbose_name,
                                         s_models=_s_models,
                                         last_field_name=_field_name):
                yield i
        else:
            # _model_verbose_name = verbose_name_prefix or str(model._meta.verbose_name)
            if _name_prefix:
                key = LOOKUP_SEP.join((_name_prefix, field.name))
            else:
                key = field.name

            value = f"{_name_prefix.title()}'s {field.verbose_name.title()}"

            yield (key, value)


