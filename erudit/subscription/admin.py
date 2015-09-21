from django.contrib import admin
from subscription.models import (
    Client, Product, RenewalNotice
)

# Register your models here.
admin.site.register(Product)
admin.site.register(Client)
admin.site.register(RenewalNotice)
