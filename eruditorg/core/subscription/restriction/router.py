from django.conf import settings

# The MANAGED const is set to True when testing so that we have a DB schema to put or test models
# in it.
MANAGED = getattr(settings, "RESTRICTION_MODELS_ARE_MANAGED", False)


class RestrictionRouter:
    def db_for_read(self, model, **hints):
        if MANAGED:
            return "default"
        if model._meta.app_label == "restriction":
            return "restriction"
        return None
