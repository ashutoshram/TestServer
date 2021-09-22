from django.contrib import admin
from django.utils.safestring import mark_safe
from django.forms import Widget
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, F, Count
from django.db.models.fields import NOT_PROVIDED
import mimetypes
from django.db import models
from django.core.exceptions import ValidationError
import datetime
import uuid
from rs4.attrdict import AttrDict
from sqlphile.sql import SQL, D
from sqlphile.q import _Q
from sqlphile.model import AbstractModel

def set_title (title):
    admin.site.site_title = title
    admin.site.site_header = "{}".format (title)
    admin.site.index_title = "{} Management Console".format (title)

# widgets -----------------------------------------------------
def get_type (path):
    return mimemodels.guess_type (os.path.basename (path))[0]

def ImageWidget (width = 360):
    class _ImageWidget(Widget):
        def render(self, name, value, **noneed):
            return value and mark_safe ('<img src="{}" width="{}">'.format (value, width)) or 'No Image'
    return _ImageWidget

class LinkWidget(Widget):
    def render(self, name, value, **noneed):
        return value and mark_safe ('<a href="{}">{}</a> [<a href="{}" target="_blank">새창</a>]'.format (value, value, value)) or 'No Image'

def VideoWidget (video_width = 320, video_height = 240):
    class _VideoWidget(Widget):
        def render(self, name, value, **noneed):
            return value and mark_safe (
                '<video width="{}" height="{}" controls><source src="{}" type="{}"></video>'.format (
                    video_width, video_height, value, get_type (value)
                )
            ) or 'No Video'
    return _VideoWidget

class AudioWidget(Widget):
    def render(self, name, value, **noneed):
        return value and mark_safe ('<audio controls><source src="{}" type="{}"></audio>'.format (
            value, get_type (value)
            )
        ) or 'No Audio'


# filter prototypes -------------------------------------------
class CountFilter(SimpleListFilter):
    title = None
    parameter_name = None
    _countable_realted_name = None
    _filter = {}
    _options = [1,3,5,10,20,30]

    def create_action_count_filter (self):
        return [(i, 'Above {}'.format (i)) for i in self._options]

    def lookups (self, request, model_admin):
        return self.create_action_count_filter ()

    def queryset (self, request, queryset):
        value = self.value()
        if value:
            return queryset.select_related ().annotate (buy_count = Count (self._countable_realted_name, **self._filter)).filter (buy_count__gt = value)
        return queryset


class NullFilter (SimpleListFilter):
    title = None
    parameter_name = None
    _field_name = None
    _options = {'NULL': 'Null', 'NOTNULL': 'Not Null'}

    def lookups (self, request, model_admin):
        return [('t', self._options ['NULL']), ('f', self._options ['NOTNULL'])]

    def queryset (self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter (**{'{}__isnull'.format (self._field_name): value == 't' and True or False})
        return queryset


class StackedInline (admin.StackedInline):
    can_delete = False
    show_change_link = True


# model admin -------------------------------------------
class ModelAdmin (admin.ModelAdmin):
    image_width = 320
    video_width = 320
    enable_add = True
    enable_delete = True
    enable_change = True

    list_per_page = 100
    list_max_show_all = 200

    def has_add_permission(self, request, obj=None):
        return self.enable_add

    def has_delete_permission(self, request, obj=None):
        return self.enable_delete

    def has_change_permission(self, request, obj=None):
        return self.enable_change

    def before_changelist_view (self, queryset, context):
        pass

    def changelist_view (self, request, extra_context = None):
        r = super ().changelist_view (request)
        if hasattr (r, 'context_data') and 'cl' in r.context_data:
            self.before_changelist_view (r.context_data ['cl'].queryset, r.context_data)
        return r

    def save_model (self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def formfield_for_dbfield (self, db_field, request, **kwargs):
        if 'widget' not in kwargs:
            if db_field.name.endswith ('image'):
                kwargs ['widget'] = ImageWidget (self.image_width)
                return db_field.formfield(**kwargs)
            elif db_field.name.endswith ('video'):
                kwargs ['widget'] = VideoWidget (self.video_width)
                return db_field.formfield(**kwargs)
            elif db_field.name.endswith ('audio'):
                kwargs ['widget'] = AudioWidget
                return db_field.formfield(**kwargs)
            elif db_field.name.endswith ('url'):
                kwargs ['widget'] = LinkWidget
                return db_field.formfield(**kwargs)
        return super ().formfield_for_dbfield (db_field, request, **kwargs)

