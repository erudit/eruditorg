# -*- coding: utf-8 -*-

import io

from django import template
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.encoding import force_bytes
from django.utils.translation import gettext as _
from eruditarticle.utils import remove_xml_namespaces
from PyPDF2 import PdfFileReader
from lxml import etree as et

register = template.Library()


@register.filter
def format_article_html_title(article):
    """ Formats the article html title

    Display the html_title if it exists otherwise display "untitled"
    """
    if article.html_title:
        return mark_safe(article.html_title)
    else:
        return _("[Article sans titre]")


@register.filter
def format_article_title(article):
    """ Formats the article title

    Display the title if it exists otherwise display "untitled"
    """
    return article.title if article.title else _("[Article sans titre]")


@register.filter
def join_author_list(author_list):
    author_list = list(author_list)
    if not author_list:
        return ""
    first_author = author_list.pop(0)
    if not author_list:
        return _('Avec {first_author}'.format(first_author=first_author))

    last_author = author_list.pop(len(author_list) - 1)
    if not author_list:
        return _('Avec {first_author} et {last_author}'.format(
            first_author=first_author, last_author=last_author
        ))

    return _('Avec {first_author}, {contributors} et {last_author}').format(
        first_author=first_author,
        contributors=", ".join(str(author) for author in author_list),
        last_author=last_author
    )


@register.simple_tag(takes_context=True)
def render_article(context, article, only_summary=False):
    """ Renders the given article instance as HTML. """
    # Tries to fetch the HTML content of the article from the cache

    context['only_summary'] = only_summary
    if 'article' not in context:
        context['article'] = article

    if article.fedora_object.pdf.exists:
        pdf = PdfFileReader(article.fedora_object.pdf.content)
        context['pdf_exists'] = True
        context['pdf_num_pages'] = pdf.getNumPages()
        context['can_display_first_pdf_page'] = (
            context['pdf_exists'] and
            context['pdf_num_pages'] > 1
        )

    # Prepares the XML of the article
    article_xml = remove_xml_namespaces(et.fromstring(article.fedora_object.xml_content))

    # Renders the templates corresponding to the XSL stylesheet that
    # will allow us to convert ERUDITXSD300 articles to HTML
    xsl_template = loader.get_template('public/journal/eruditxsd300_to_html.xsl')
    xsl = xsl_template.render(context.flatten() if hasattr(context, 'flatten') else context)

    # Performs the XSLT transformation
    lxsl = et.parse(io.BytesIO(force_bytes(xsl)))
    html_transform = et.XSLT(lxsl)
    html_content = html_transform(article_xml)

    return mark_safe(html_content)
