# -*- coding: utf-8 -*-


class RestrictionRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'restriction':
            return 'restriction'
        return None
