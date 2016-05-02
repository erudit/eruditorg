# -*- coding: utf-8 -*-

from django.contrib.sites.models import Site
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import ugettext_lazy as _


class EruditRssFeedGenerator(Rss201rev2Feed):
    """ Adds the Érudit logo to a RSS feed. """
    def add_root_elements(self, handler):
        super(EruditRssFeedGenerator, self).add_root_elements(handler)
        handler.addQuickElement(
            'image', '', {
                 'url': static('erudit-header.jpg'),
                 'title': _('Érudit'),
                 'link': 'http://{domain}/'.format(domain=Site.objects.get_current().domain),
             })
