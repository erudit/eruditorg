class LegacyRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'individual_subscription':
            return 'legacy_individual_subscription'
        return 'default'
