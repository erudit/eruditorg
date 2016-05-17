class LegacyRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'legacy':
            return 'legacy_subscription'
        return None
