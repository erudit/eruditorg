from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from rules.permissions import permissions

from .models import Rule
from .forms import RuleForm


class RuleAdmin(admin.ModelAdmin):
    form = RuleForm
    list_display = (
        'id',
        'user',
        'group',
        'permission',
        'content_type',
        '_content_object',
        'date_modification',
        'date_creation',

    )
    list_filter = ('content_type', )

    def _content_object(self, obj):
        if not obj.content_object:
            return
        else:
            return str(obj.content_object)
    _content_object.short_description = _("Objet")
    _content_object.allow_tags = True

admin.site.register(Rule, RuleAdmin)


class RuleInline(GenericTabularInline):
    model = Rule
    extra = 0
    permission_filters = ()

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Filter permissions according context permissions available
        """
        if db_field.name == 'permission':
            already = [c[0] for c in db_field.choices]
            choices = [(k, _(k)) for k in permissions.keys()]
            new = [item for item in choices if item[0] in
                   self.permission_filters and item[0] not in already]
            db_field.choices.extend(new)
        return super(RuleInline, self).formfield_for_dbfield(db_field, **kwargs)
