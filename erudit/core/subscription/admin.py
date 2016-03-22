# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import InstitutionIPAddressRange
from .models import JournalAccessSubscription
from .models import JournalManagementPlan
from .models import JournalManagementSubscription


admin.site.register(InstitutionIPAddressRange)
admin.site.register(JournalAccessSubscription)
admin.site.register(JournalManagementPlan)
admin.site.register(JournalManagementSubscription)
