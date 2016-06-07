# -*- coding: utf-8 -*-

from django.contrib import admin

from ..models import Grant
from ..models import GrantingAgency


admin.site.register(Grant)
admin.site.register(GrantingAgency)
