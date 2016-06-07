# -*- coding: utf-8 -*-

from django.contrib import admin

from erudit.models import Basket
from erudit.models import SubscriptionPrice
from erudit.models import SubscriptionType
from erudit.models import SubscriptionZone


admin.site.register(Basket)
admin.site.register(SubscriptionPrice)
admin.site.register(SubscriptionType)
admin.site.register(SubscriptionZone)
