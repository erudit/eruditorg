from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from rangefilter.filter import DateRangeFilter


class HasPasswordListFilter(admin.SimpleListFilter):
    title = _("Mot de passe défini")
    parameter_name = "has_password"

    def lookups(self, resquest, model_admin):
        return (
            ("1", _("Yes")),
            ("0", _("No")),
        )

    def queryset(self, request, queryset):
        has_password = request.GET.get("has_password")
        no_password_query = Q(password="") | Q(password__startswith=UNUSABLE_PASSWORD_PREFIX)
        if has_password == "1":
            return queryset.exclude(no_password_query)
        elif has_password == "0":
            return queryset.filter(no_password_query)
        else:
            return queryset


class UserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "date_joined",
        "last_login",
        "has_password",
        "is_staff",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        ("date_joined", DateRangeFilter),
        ("last_login", DateRangeFilter),
        HasPasswordListFilter,
    )

    def has_password(self, user):
        return bool(user.password and not user.password.startswith(UNUSABLE_PASSWORD_PREFIX))

    has_password.boolean = True
    has_password.admin_order_field = "password"
    has_password.short_description = _("Mot de passe défini")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
