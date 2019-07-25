import io
import datetime
import re

from bs4 import BeautifulSoup, Tag
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext as _, get_language
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Image, KeepInFrame, Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus.tables import Table, TableStyle
from urllib.parse import urlparse

from erudit.models.journal import Article
from erudit.fedora.cache import get_cached_datastream_content


STATIC_ROOT = str(Path(__file__).parents[3] / 'static')

# Fonts.
FONTS_DIR = STATIC_ROOT + '/fonts/Spectral'
pdfmetrics.registerFont(TTFont('Spectral', FONTS_DIR + '/Spectral-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Spectral-Bold', FONTS_DIR + '/Spectral-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Spectral-Italic', FONTS_DIR + '/Spectral-Italic.ttf'))
pdfmetrics.registerFont(TTFont('Spectral-BoldItalic', FONTS_DIR + '/Spectral-BoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('SpectralSC', FONTS_DIR + '/SpectralSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('SpectralSC-Bold', FONTS_DIR + '/SpectralSC-Bold.ttf'))
pdfmetrics.registerFont(TTFont('SpectralSC-Italic', FONTS_DIR + '/SpectralSC-Italic.ttf'))
pdfmetrics.registerFont(TTFont('SpectralSC-BoldItalic', FONTS_DIR + '/SpectralSC-BoldItalic.ttf'))
pdfmetrics.registerFontFamily(
    'Spectral',
    normal='Spectral',
    bold='Spectral-Bold',
    italic='Spectral-Italic',
    boldItalic='Spectral-BoldItalic',
)
pdfmetrics.registerFontFamily(
    'SpectralSC',
    normal='SpectralSC',
    bold='SpectralSC-Bold',
    italic='SpectralSC-Italic',
    boldItalic='SpectralSC-BoldItalic',
)
addMapping('Spectral', 0, 0, 'Spectral')
addMapping('Spectral-Bold', 1, 0, 'Spectral Bold')
addMapping('Spectral-Italic', 0, 1, 'Spectral Italic')
addMapping('Spectral-BoldItalic', 1, 1, 'Spectral Bold Italic')
addMapping('SpectralSC', 0, 0, 'SpectralSC')
addMapping('SpectralSC-Bold', 1, 0, 'SpectralSC Bold')
addMapping('SpectralSC-Italic', 0, 1, 'SpectralSC Italic')
addMapping('SpectralSC-BoldItalic', 1, 1, 'SpectralSC Bold Italic')


def get_coverpage(article):
    pdf_buffer = io.BytesIO()
    template = SimpleDocTemplate(
        pdf_buffer,
        # Letter size: 612 points by 792 points
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
        title=article.html_title,
        author=article.get_formatted_authors_without_suffixes(),
        creator='Érudit',
        subject='',
    )
    language = get_language()

    # Lines & spacers
    black_line = Line(colors.black, 542, 1)
    grey_line = Line(colors.lightgrey, 542, 1)
    grey_half_line = Line(colors.lightgrey, 261, 1)
    small_spacer = Spacer(0.25, 2.5)
    medium_spacer = Spacer(0.25, 5)
    large_spacer = Spacer(0.25, 10)
    extra_large_spacer = Spacer(0.25, 20)

    # Text styles.
    styles = get_stylesheet()

    # Text.
    story = []

    # -----------------------------------------------------------------------------
    # INFO

    # PDF creation date & time.
    story.append(Paragraph(
        _('Document généré le %(now_dt)s') % {
            'now_dt': formats.date_format(
                datetime.datetime.now(tz=timezone.get_current_timezone()),
                'SHORT_DATETIME_FORMAT'
            ),
        },
        styles['small_grey'],
    ))

    # Black line.
    story.append(medium_spacer)
    story.append(black_line)
    story.append(medium_spacer)

    # Erudit objects.
    article_erudit_object = article.get_erudit_object()
    issue_erudit_object = article.issue.get_erudit_object()

    # -----------------------------------------------------------------------------
    # HEADER

    header = []

    # Journal main title.
    journal_titles = issue_erudit_object.get_titles()
    journal_main_title = journal_titles.get('main')
    header.append(Paragraph(
        journal_main_title.title,
        styles['h3'],
    ))
    # Journal main subtitle.
    if journal_main_title.subtitle:
        header.append(Paragraph(
            journal_main_title.subtitle,
            styles['h4'],
        ))

    # Journal parallel titles.
    for journal_paral_title in journal_titles.get('paral'):
        if journal_main_title.title != journal_paral_title.title:
            header.append(small_spacer)
            header.append(Paragraph(
                journal_paral_title.title,
                styles['h3'],
            ))
        # Journal parallel subtitles.
        if journal_paral_title.subtitle:
            header.append(Paragraph(
                journal_paral_title.subtitle,
                styles['h4'],
            ))
    header.append(extra_large_spacer)

    # Article titles.
    titles = article_erudit_object.get_titles()
    if titles['main'].title is None and not titles['reviewed_works']:
        header.append(Paragraph(
            _('[Article sans titre]'),
            styles['h1'],
        ))
    if titles['main'].title:
        header.append(Paragraph(
            clean(titles['main'].title, small_caps_font='SpectralSC-Bold'),
            styles['h1'],
        ))
        if titles['main'].subtitle:
            header.append(Paragraph(
                clean(titles['main'].subtitle, small_caps_font='SpectralSC-Bold'),
                styles['h1_grey'],
            ))
        for title in titles['paral'] + titles['equivalent']:
            header.append(small_spacer)
            header.append(Paragraph(
                clean(title.title, small_caps_font='SpectralSC-Bold'),
                styles['h1'] if title.subtitle else styles['h1_grey'],
            ))
            if title.subtitle:
                header.append(Paragraph(
                    clean(title.subtitle, small_caps_font='SpectralSC-Bold'),
                    styles['h1_grey'],
                ))
    for title in titles['reviewed_works']:
        header.append(small_spacer)
        header.append(Paragraph(
            clean(title, small_caps_font='SpectralSC-Bold'),
            styles['h1_grey'],
        ))
    header.append(large_spacer)

    # Article authors.
    header.append(Paragraph(
        article.get_formatted_authors_without_suffixes(),
        styles['h2'],
    ))

    # Journal path.
    journal_path = reverse('public:journal:journal_detail', kwargs={
        'code': article.issue.journal.code,
    })
    # Journal logo.
    journal_logo_ds = get_cached_datastream_content(article.issue.journal.fedora_object, 'logo')
    if journal_logo_ds is not None:
        journal_logo = HyperlinkedImage(
            journal_logo_ds,
            hyperlink='https://www.erudit.org{}'.format(journal_path),
        )
        # Resize journal logo if it's wider than 80 points.
        journal_logo._restrictSize(80, 220)
    else:
        journal_logo = []
    header_table = Table(
        [(KeepInFrame(472, 220, header), journal_logo)],
        colWidths=(462, 90),
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(header_table)

    # Grey line.
    story.append(large_spacer)
    story.append(grey_line)
    story.append(large_spacer)

    # -----------------------------------------------------------------------------
    # BODY

    # Left column.
    left_column = []

    # Issue themes.
    themes = issue_erudit_object.get_themes(formatted=True, html=True)
    if themes:
        for index, theme in enumerate(themes[0]['names']):
            left_column.append(Paragraph(
                clean(theme),
                styles['normal'] if index == 0 else styles['normal_grey'],
            ))
        left_column.append(small_spacer)

    # Volume title.
    left_column.append(Paragraph(
        article.issue.volume_title,
        styles['normal'],
    ))
    left_column.append(large_spacer)

    # URI & DOI.
    left_column.append(Paragraph(
        '{label} <link href="{url}" color="#ff4242">{url}</link>'.format(
            label=_('URI&nbsp;:'),
            url='https://id.erudit.org/iderudit/{path}'.format(
                path=article.localidentifier
            )
        ),
        styles['normal'],
    ))
    if article.doi:
        left_column.append(Paragraph(
            '{label} <link href="{url}" color="#ff4242">{url}</link>'.format(
                label=_('DOI&nbsp;:'),
                url='https://doi.org/{path}'.format(
                    path=article.doi
                )
            ),
            styles['normal'],
        ))
    left_column.append(large_spacer)

    # Issue summary link.
    issue_path = reverse('public:journal:issue_detail', kwargs={
        'journal_code': article.issue.journal.code,
        'issue_slug': article.issue.volume_slug,
        'localidentifier': article.issue.localidentifier,
    })
    left_column.append(Paragraph(
        '<link href="{url}" color="#ff4242">{text}</link>'.format(
            url='https://www.erudit.org{}'.format(
                issue_path
            ),
            text=_('Aller au sommaire du numéro'),
        ),
        styles['normal'],
    ))

    # Grey line.
    left_column.append(large_spacer)
    left_column.append(grey_half_line)
    left_column.append(large_spacer)

    # Publishers.
    left_column.append(Paragraph(
        _('Éditeur(s)'),
        styles['normal'],
    ))
    left_column.append(medium_spacer)
    for publisher in article_erudit_object.publishers:
        left_column.append(Paragraph(
            publisher,
            styles['small'],
        ))
    left_column.append(large_spacer)

    # ISSN
    if article.issue.journal.issn_print or article.issue.journal.issn_web:
        left_column.append(Paragraph(
            _('ISSN'),
            styles['normal'],
        ))
    left_column.append(medium_spacer)
    if article.issue.journal.issn_print:
        left_column.append(Paragraph(
            '{issn} ({label})'.format(
                issn=article.issue.journal.issn_print,
                label=_('imprimé'),
            ),
            styles['small'],
        ))
    if article.issue.journal.issn_web:
        left_column.append(Paragraph(
            '{issn} ({label})'.format(
                issn=article.issue.journal.issn_web,
                label=_('numérique'),
            ),
            styles['small'],
        ))
    left_column.append(large_spacer)

    # Journal link.
    left_column.append(Paragraph(
        '<link href="{url}" color="#ff4242">{text}</link>'.format(
            url='https://www.erudit.org{}'.format(
                journal_path
            ),
            text=_('Découvrir la revue'),
        ),
        styles['normal'],
    ))

    # Grey line.
    left_column.append(large_spacer)
    left_column.append(grey_half_line)
    left_column.append(large_spacer)

    cite_strings = {
        Article.ARTICLE_DEFAULT: _('Citer cet article'),
        Article.ARTICLE_REPORT: _('Citer ce compte rendu'),
        Article.ARTICLE_OTHER: _('Citer ce document'),
        Article.ARTICLE_NOTE: _('Citer cette note'),
    }

    # Cite this article.
    left_column.append(Paragraph(
        cite_strings.get(article.type),
        styles['normal'],
    ))
    left_column.append(medium_spacer)
    left_column.append(Paragraph(
        clean(article.cite_string_apa),
        styles['small'],
    ))

    # Right column.
    right_column = []

    # Abstracts.
    if article.html_abstract:
        right_column.append(Paragraph(
            _("Résumé de l'article"),
            styles['normal'],
        ))
        right_column.append(medium_spacer)
        soup = BeautifulSoup(article.html_abstract, features='html.parser')
        for paragraph in soup.find_all('p'):
            right_column.append(Paragraph(
                clean(paragraph),
                styles['small'],
            ))
            right_column.append(small_spacer)

    # Body table.
    body_table = Table(
        [(KeepInFrame(276, 350, left_column), KeepInFrame(276, 350, right_column))],
        colWidths=276,
        rowHeights=350
    )
    body_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(body_table)

    # -----------------------------------------------------------------------------
    # FOOTER

    # Copyrights.
    copyrights = []
    copyrights.append(small_spacer)
    for copyright in article.copyrights:
        if 'text' in copyright:
            copyrights.append(Paragraph(
                copyright['text'],
                styles['small'],
            ))
            copyrights.append(small_spacer)
        elif 'href' in copyright and 'img' in copyright:
            try:
                parsed = urlparse(copyright['img'])
                path = STATIC_ROOT + '/img/licensebuttons.net/' + parsed.path
                image = HyperlinkedImage(path, hyperlink=copyright['href'])
                # Resize license logo if it's wider than 50 points.
                image._restrictSize(50, 35)
                copyrights.append(image)
                copyrights.append(small_spacer)
            except OSError:
                pass
    copyrights = KeepInFrame(271, 55, copyrights)

    # Policy.
    policy_urls = {
        'fr': 'https://apropos.erudit.org/fr/usagers/politique-dutilisation/',
        'en': 'https://apropos.erudit.org/en/users/policy-on-use/',
    }
    statement = []
    statement.append(small_spacer)
    statement.append(Paragraph(
        _('Ce document est protégé par la loi sur le droit d’auteur. L’utilisation des services \
        d’Érudit (y compris la reproduction) est assujettie à sa politique d’utilisation que vous \
        pouvez consulter en ligne.'),
        styles['small'],
    ))
    statement.append(small_spacer)
    statement.append(Paragraph(
        '<link href="{url}" color="#ff4242">{url}</link>'.format(
            url=policy_urls[language]
        ),
        styles['small'],
    ))
    statement.append(small_spacer)

    # Mission.
    mission = []
    mission.append(small_spacer)
    mission.append(Paragraph(
        _('Cet article est diffusé et préservé par Érudit.'),
        styles['small'],
    ))
    mission.append(small_spacer)
    mission.append(Paragraph(
        _('Érudit est un consortium interuniversitaire sans but lucratif composé de l’Université de \
        Montréal, l’Université Laval et l’Université du Québec à Montréal. Il a pour mission la \
        promotion et la valorisation de la recherche.'),
        styles['small_grey'],
    ))
    mission.append(small_spacer)
    mission.append(Paragraph(
        '<link href="{url}" color="#ff4242">{url}</link>'.format(
            url='https://www.erudit.org/{lang}/'.format(
                lang=language
            )
        ),
        styles['small'],
    ))
    mission.append(small_spacer)

    # Logo.
    logo = []
    logo.append(small_spacer)
    logo.append(HyperlinkedImage(
        STATIC_ROOT + '/img/logo-erudit.png',
        hyperlink='https://www.erudit.org/{lang}/'.format(lang=language),
        width=75.75,
        height=25,
    ))
    logo.append(small_spacer)

    # Footer table
    footer_table = Table(
        [(copyrights, statement), (logo, mission)],
        colWidths=271,
        rowHeights=55,
    )
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.lightgrey),
        ('LINEABOVE', (0, 1), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))

    def footer_content(canvas, document):
        canvas.saveState()
        footer_table.wrap(271, document.bottomMargin)
        footer_table.drawOn(canvas, 35, 15)
        canvas.restoreState()

    # -----------------------------------------------------------------------------
    # BUILD COVERPAGE

    template.build(story, onFirstPage=footer_content)
    return pdf_buffer


def get_stylesheet():
    stylesheet = StyleSheet1()
    stylesheet.add(ParagraphStyle(
        name='normal',
        fontName='Spectral',
        fontSize=8,
        leading=10,
    ))
    stylesheet.add(ParagraphStyle(
        name='bold',
        parent=stylesheet['normal'],
        fontName='Spectral-Bold',
    ))
    stylesheet.add(ParagraphStyle(
        name='italic',
        parent=stylesheet['normal'],
        fontName='Spectral-Italic',
    ))
    stylesheet.add(ParagraphStyle(
        name='blod_italic',
        parent=stylesheet['normal'],
        fontName='Spectral-BoldItalic',
    ))
    stylesheet.add(ParagraphStyle(
        name='h1',
        parent=stylesheet['bold'],
        fontSize=14,
        leading=16,
    ))
    stylesheet.add(ParagraphStyle(
        name='h2',
        parent=stylesheet['normal'],
        fontSize=12,
        leading=14,
    ))
    stylesheet.add(ParagraphStyle(
        name='h3',
        parent=stylesheet['bold'],
        fontSize=12,
        leading=14,
    ))
    stylesheet.add(ParagraphStyle(
        name='h4',
        parent=stylesheet['bold'],
        fontSize=10,
        leading=12,
        textColor=colors.grey,
    ))
    stylesheet.add(ParagraphStyle(
        name='small',
        parent=stylesheet['normal'],
        fontSize=7,
        leading=9,
    ))
    stylesheet.add(ParagraphStyle(
        name='small_grey',
        parent=stylesheet['small'],
        textColor=colors.grey,
    ))
    stylesheet.add(ParagraphStyle(
        name='h1_grey',
        parent=stylesheet['h1'],
        textColor=colors.grey,
    ))
    stylesheet.add(ParagraphStyle(
        name='normal_grey',
        parent=stylesheet['normal'],
        textColor=colors.grey,
    ))
    return stylesheet


def clean(text, small_caps_font='SpectralSC'):
    soup = text if isinstance(text, Tag) else BeautifulSoup(text, 'html.parser')
    # Replace <span class="barre"> by <strike>
    for node in soup.find_all('span', attrs={'class': 'barre'}):
        del node['class']
        node.name = 'strike'
    # Replace <span class="souligne"> by <u>
    for node in soup.find_all('span', attrs={'class': 'souligne'}):
        del node['class']
        node.name = 'u'
    # Uppercase <span class="majuscule"> nodes.
    for node in soup.find_all('span', attrs={'class': 'majuscule'}):
        del node['class']
        node.replace_with(node.text.upper())
    # Change the font of <span class="petitecap'> nodes.
    for node in soup.find_all('span', attrs={'class': 'petitecap'}):
        del node['class']
        node['fontName'] = small_caps_font
    # Remove any footnotes.
    for node in soup.find_all('a', attrs={'class': 'norenvoi'}):
        node.decompose()
    # Remove all other classes we can't transform.
    for node in soup.find_all('span', attrs={'class': re.compile('.*')}):
        del node['class']
    return str(soup)


class Line(Flowable):

    def __init__(self, color, width, height):
        Flowable.__init__(self)
        self.color = color
        self.width = width
        self.height = height

    def __repr__(self):
        return 'Line(color=%s, width=%s, height=%s)'.format(
            self.color,
            self.width,
            self.height,
        )

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.line(0, self.height, self.width, 0)


class HyperlinkedImage(Image):

    def __init__(self, filename, width=None, height=None, kind='direct', mask='auto', lazy=1,
                 hAlign='LEFT', hyperlink=None):
        self.hyperlink = hyperlink
        super(HyperlinkedImage, self).__init__(filename, width, height, kind, mask, lazy, hAlign)

    def drawOn(self, canvas, x, y, _sW=0):
        if self.hyperlink:
            x1 = self._hAlignAdjust(x, _sW)
            y1 = y
            x2 = x1 + self.drawWidth
            y2 = y1 + self.drawHeight
            canvas.linkURL(url=self.hyperlink, rect=(x1, y1, x2, y2), thickness=0, relative=1)
        super(HyperlinkedImage, self).drawOn(canvas, x, y, _sW)
