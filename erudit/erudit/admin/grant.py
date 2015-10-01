from django.contrib import admin

from erudit.models import GrantingAgency, Grant

admin.site.register(GrantingAgency)
admin.site.register(Grant)
