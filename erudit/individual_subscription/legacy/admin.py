from django.apps import apps
from django.contrib import admin


class VerboseModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(VerboseModelAdmin, self).__init__(model, admin_site)

for model in apps.get_app_config('individual_subscription').get_models():
    try:
        admin.site.register(model, VerboseModelAdmin)
    except:
        pass
