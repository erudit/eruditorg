from django.contrib import admin

from erudit.models import (
    SubscriptionPrice,
    SubscriptionType,
    SubscriptionZone,
    Basket,
)


admin.site.register(SubscriptionPrice)
admin.site.register(SubscriptionType)
admin.site.register(SubscriptionZone)
admin.site.register(Basket)
