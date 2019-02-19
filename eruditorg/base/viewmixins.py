import inspect

from django.views.decorators.cache import cache_page
from django.utils.translation import activate


class CacheMixin:
    """ Caches the result of a view for a specific number of seconds. """
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(
            self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


class MenuItemMixin:
    """
    This mixins injects attributes that start with the 'menu_' prefix into
    the context generated by the view it is applied to.
    This behavior can be used to highlight an item of a navigation component.
    """
    def get_context_data(self, **kwargs):
        context = super(MenuItemMixin, self).get_context_data(**kwargs)
        vattrs = inspect.getmembers(self, lambda a: not(inspect.isroutine(a)))
        menu_kwargs = dict(a for a in vattrs if a[0].startswith('menu_'))
        context.update(menu_kwargs)
        return context


class ActivateLegacyLanguageViewMixin:
    """ """

    def activate_legacy_language(self, *args, **kwargs):
        if 'lang' in kwargs and kwargs['lang'] == 'en' or self.request.GET.get('lang') == 'en':
            activate('en')
        else:
            activate('fr')
