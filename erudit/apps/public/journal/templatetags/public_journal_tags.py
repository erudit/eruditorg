# -*- coding: utf-8 -*-

import io

from django import template
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.encoding import force_bytes
from eruditarticle.utils import remove_xml_namespaces
from lxml import etree as et

register = template.Library()


@register.simple_tag(takes_context=True)
def render_article(context, article):
    """
    Renders the given article instance as HTML.
    """
    # Prepares the XML of the article
    article_xml = remove_xml_namespaces(et.fromstring(article.fedora_object.xml_content))

    # Renders the templates corresponding to the XSL stylesheet that
    # will allow us to convert ERUDITXSD300 articles to HTML
    xsl_template = loader.get_template('public/journal/eruditxsd300_to_html.xsl')
    xsl = xsl_template.render(context)

    # Performs the XSLT transformation
    lxsl = et.parse(io.BytesIO(force_bytes(xsl)))
    html_transform = et.XSLT(lxsl)

    return mark_safe(html_transform(article_xml))
