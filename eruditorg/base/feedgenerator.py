from django.templatetags.static import static
from django.utils.feedgenerator import Rss201rev2Feed


class EruditRssFeedGenerator(Rss201rev2Feed):
    """ Adds the Érudit logo to a RSS feed. """

    def add_root_elements(self, handler):
        super(EruditRssFeedGenerator, self).add_root_elements(handler)
        handler.startElement("image", {})
        handler.addQuickElement("url", static("img/logo-erudit.png"))
        handler.addQuickElement("title", "Érudit")
        handler.addQuickElement("link", "https://erudit.org")
        handler.endElement("image")
