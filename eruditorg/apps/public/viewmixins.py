from urllib.parse import urlencode
from django.conf import settings
from django.utils.translation import get_language


class FallbackBaseViewMixin:
    """ Mixin for views that offer a fallback to erudit's classic website """

    def get_fallback_url(self):
        """ Returns the classic website url for this view """
        return None

    def get_fallback_querystring_dict(self):
        return {'lang': get_language()}

    def get_context_data(self, **kwargs):
        """ Adds the classic website url in context """
        context = super().get_context_data(**kwargs)
        fallback_url = self.get_fallback_url()
        if fallback_url:
            querystring_dict = self.get_fallback_querystring_dict()
            if 'ticket' not in querystring_dict:
                return context
            if not fallback_url.startswith('http'):
                fallback_url = settings.FALLBACK_BASE_URL + fallback_url
            context['fallback_url'] = "{fallback_url}?{querystring}".format(
                fallback_url=fallback_url,
                querystring=urlencode(querystring_dict)
            )

        return context


class FallbackAbsoluteUrlViewMixin(FallbackBaseViewMixin):

    fallback_url = None

    def get_fallback_url(self):
        """ Returns the classic website url for this view """
        return self.fallback_url


class FallbackObjectViewMixin(FallbackBaseViewMixin):

    fallback_url_format = None
    fallback_object_property = None

    def get_fallback_url_format_kwargs(self):
        return {}

    def get_fallback_url_format(self):
        return self.fallback_url_format

    def get_fallback_url(self):
        fallback_url_format = self.get_fallback_url_format()
        if not fallback_url_format:
            return None
        return fallback_url_format.format(
            **self.get_fallback_url_format_kwargs()
        )
