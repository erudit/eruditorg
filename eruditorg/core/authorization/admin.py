# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .defaults import AuthorizationConfig
from .models import Authorization


class AuthorizationAdminForm(forms.ModelForm):
    class Meta:
        model = Authorization
        exclude = []

    def __init__(self, *args, **kwargs):
        super(AuthorizationAdminForm, self).__init__(*args, **kwargs)
        self.fields['authorization_codename'].choices += AuthorizationConfig.get_choices(
            staff_only=True)


class AuthorizationAdmin(admin.ModelAdmin):
    form = AuthorizationAdminForm
    list_display = (
        'id',
        'user',
        'group',
        'authorization_codename',
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

    _content_object.short_description = _('Objet')
    _content_object.allow_tags = True


admin.site.register(Authorization, AuthorizationAdmin)
