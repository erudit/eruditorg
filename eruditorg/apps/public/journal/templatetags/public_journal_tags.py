# -*- coding: utf-8 -*-

import io

from django import template
from django.core.cache import cache
from django.template import loader
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.encoding import force_bytes
from eruditarticle.utils import remove_xml_namespaces
from lxml import etree as et

from ..conf import settings as journal_settings

register = template.Library()


@register.simple_tag(takes_context=True)
def render_article(context, article):
    """ Renders the given article instance as HTML. """
    # Tries to fetch the HTML content of the article from the cache
    cache_key = 'article-html-content-{article_id}-{lang}'.format(
        article_id=article.id, lang=translation.get_language())
    html_content = cache.get(cache_key, None) if journal_settings.ARTICLE_HTML_CONTENT_USE_CACHE \
        else None

    if 'article' not in context:
        context['article'] = article

    if html_content is None:
        # Prepares the XML of the article
        article_xml = remove_xml_namespaces(et.fromstring(article.fedora_object.xml_content))

        # Renders the templates corresponding to the XSL stylesheet that
        # will allow us to convert ERUDITXSD300 articles to HTML
        xsl_template = loader.get_template('public/journal/eruditxsd300_to_html.xsl')
        xsl = xsl_template.render(context.flatten())

        # Performs the XSLT transformation
        lxsl = et.parse(io.BytesIO(force_bytes(xsl)))
        html_transform = et.XSLT(lxsl)
        html_content = html_transform(article_xml)

        # Updates the cache
        cache.set(
            cache_key, str(html_content), journal_settings.ARTICLE_HTML_CONTENT_CACHE_TIMEOUT)

    return mark_safe(html_content)


@register.filter
def author_articles(author, journal):
    """ Returns all the articles of the author in the considered journal. """
    return author.articles_in_journal(journal)


@register.filter
def sort_by_ordseq(erudit_objects):
    """ Returns the erudit objects (issues or articles) sorted by their ordering number. """
    return sorted(erudit_objects, key=lambda a: a.erudit_object.ordseq)
