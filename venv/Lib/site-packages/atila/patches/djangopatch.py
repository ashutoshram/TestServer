from django.db.models.fields import NOT_PROVIDED
from django.db import models
from django.core.exceptions import ValidationError
import datetime
import uuid
from rs4.attrdict import AttrDict
from sqlphile.sql import SQL, D
from sqlphile.q import _Q
from sqlphile.model import AbstractModel
from skitai import was
from rs4.annotations import classproperty, override

TZ_LOCAL = datetime.datetime.now (datetime.timezone.utc).astimezone().tzinfo
TZ_UTC = datetime.timezone.utc

TYPE_MAP = [
    (models.CharField, str, 'string'),
    ((models.IntegerField, models.AutoField), int, 'integer'),
    (models.FloatField, float, 'float'),
    (models.BooleanField, bool, 'boolean'),
    (models.DateTimeField, datetime.datetime, 'datetime'),
    (models.DateField, datetime.date, 'date'),
    (models.TimeField, datetime.time, 'time'),
    (models.UUIDField, uuid.UUID, 'uuid'),
]

def utcnow ():
    return datetime.datetime.now ().astimezone (TZ_UTC)

class TableInfo:
    def __init__ (self, name, columns):
        self.name = name
        self.columns = columns
        self.pk = None
        self.fks = {}

        for field in self.columns.values ():
            if field.pk:
                self.pk = field
            if field.related_model:
                self.fks [field.name] = (field.column, field.related_model)


class Model (AbstractModel, models.Model):
    _table_info_cache = None
    _alias = '@rdb'

    class Meta:
        abstract = True

    @classmethod
    @override
    def db (cls, *args, **kargs):
        return was.db (cls._alias, *args, **kargs)

    @classmethod
    def transaction (cls):
        return cls.db (transaction = True)

    @classmethod
    @override
    def get_table_name (cls):
        return cls._meta.db_table

    @classmethod
    @override
    def get_columns (cls):
        return list (cls._get_table_info ().columns.keys ())

    @classmethod
    @override
    def get_pk (cls):
        return cls._get_table_info ().pk.column

    @classmethod
    @override
    def get_fks (cls):
        return cls._get_table_info ().fks

    @classmethod
    @override
    def validate (cls, payload, create = False):
        for fk, (column, _) in cls.get_fks ().items ():
            if fk not in payload:
                continue
            if fk == column:
                continue
            payload [column] = payload.pop (fk)

        ti = cls._get_table_info ()
        for field in ti.columns.values ():
            if field.type_name == 'datetime':
                if field.auto_now:
                    payload [field.column] = utcnow ()
                    continue
                if create and field.auto_now_add:
                    payload [field.column] = utcnow ()
                    continue

            if field.column not in payload:
                if create:
                    if field.pk:
                        continue
                    if field.default != NOT_PROVIDED:
                        payload [field.column] = field.default
                        continue
                    if field.null is False:
                        raise ValidationError ('field {} is missing'.format (field.column))
                continue

            value = payload [field.column]
            if isinstance (value, (SQL, D)):
                continue
            if field.null is False and value is None:
                raise ValidationError ('field {} should not be NULL'.format (field.column))
            if field.blank is False and value == '':
                raise ValidationError ('field {} should not be blank'.format (field.column))

            if value is None:
                continue

            if field.type and not isinstance (value, field.type):
                raise ValidationError ('field {} type should be {}'.format (field.column, field.type_name))

            if value == '' and field.null:
                payload [field.column] = value = None
                continue

            if field.choices:
                if isinstance (field.choices [0], (list, tuple)):
                    choices = [item [0] for item in field.choices]
                else:
                    choices = field.choices
                if value not in choices:
                    raise ValidationError ('field {} has invalid value'.format (field.column))

            if field.validators:
                for validate_func in field.validators:
                    validate_func (value)

        for k in payload:
            if '__' in k: # join update
                continue
            if k not in ti.columns:
                raise ValidationError ('field {} is not valid field'.format (k))

        return payload

    # private ---------------------------------------
    @classmethod
    def _get_fields (cls):
        if cls._table_info_cache is not None:
            return cls._table_info_cache.columns

        columns = {}
        for field in cls._meta.fields:
            field_type = None
            field_type_name = None
            for ftype, ptype, name in TYPE_MAP:
                if isinstance (field, ftype):
                    field_type = ptype
                    field_type_name = name
                    break

            columns [field.column] = AttrDict (dict (
                column = field.column,
                type = field_type,
                type_name = field_type_name,
                pk = field.primary_key,
                unique = field.unique,
                max_length = field.max_length,
                null = field.null,
                blank = field.blank,
                choices = field.choices,
                help_text = field.help_text,
                validators = field.validators,
                default = field.default,
                name = field.name,
                related_model = field.related_model,
                auto_now_add = field_type_name == 'datetime' and field.auto_now_add or False,
                auto_now = field_type_name == 'datetime' and field.auto_now or False
            ))
        return columns

    @classmethod
    def _get_table_info (cls):
        if cls._table_info_cache is None:
            cls._table_info_cache = TableInfo (cls.get_table_name (), cls._get_fields ())
        return cls._table_info_cache
