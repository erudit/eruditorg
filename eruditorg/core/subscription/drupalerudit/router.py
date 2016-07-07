# -*- coding: utf-8 -*-


class DrupalEruditRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'drupalerudit':
            return 'drupalerudit'
        return None
