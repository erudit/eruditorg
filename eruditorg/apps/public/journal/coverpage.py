import io

from datetime import datetime

from django.core.urlresolvers import reverse

from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.platypus import (Flowable,
                                Image,
                                SimpleDocTemplate,
                                Paragraph,
                                Spacer)
from reportlab.platypus.tables import Table, TableStyle

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(
    TTFont('Spectral', './eruditorg/static/fonts/spectral/Spectral-Regular.ttf')
)
pdfmetrics.registerFont(
    TTFont('Spectral-Italic', './eruditorg/static/fonts/spectral/Spectral-Italic.ttf')
)
pdfmetrics.registerFont(
    TTFont('Spectral-Bold', './eruditorg/static/fonts/spectral/Spectral-Bold.ttf')
)
pdfmetrics.registerFont(
    TTFont('Spectral-BoldItalic', './eruditorg/static/fonts/spectral/Spectral-BoldItalic.ttf')
)
pdfmetrics.registerFontFamily(
    'Spectral', normal='Spectral', bold='Spectral-Bold', italic='Spectral-Italic',
)

addMapping('Spectral', 0, 0, 'Spectral')
addMapping('Spectral-Italic', 0, 1, 'Spectral Italic')
addMapping('Spectral-Bold', 1, 0, 'Spectral Bold')
addMapping('Spectral-BoldItalic', 1, 1, 'Spectral Bold Italic')


class line(Flowable):

    def __init__(self, color, width, height=0):
        Flowable.__init__(self)
        self.color = color
        self.width = width
        self.height = height

    def __repr__(self):
        return "Line(w=%s)" % self.width

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.line(0, self.height, self.width, self.height)


def get_coverpage(context=None):
    buf = io.BytesIO()
    # Letter size: 612px x 792px
    c = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18
    )

    # Variables used in the doc
    Story = []
    date = "{:%B %d, %Y}".format(datetime.now())
    institution = "Université de Montréal"
    policy_url = "https://apropos.erudit.org/fr/usagers/politique-dutilisation"
    erudit_url = "https://www.erudit.org"
    erudit_logo = Image("https://gitlab.erudit.org/erudit/portail/eruditorg/raw/master/eruditorg/static/img/logo-erudit.png")
    journal_titles = [
        "HSTC Bulletin: Journal of the History of Canadian Science, Technology and \
        Medecine",
        "HSTC Bulletin : revue d’histoire des sciences, des techniques et de la \
        médecine au Canada",
    ]
    journal_url = "https://www.erudit.org"
    journal_publishers = [
        p.name for p in context['journal'].publishers.all()
    ]
    article_titles = [
        context['article'].erudit_object.get_formatted_title()
    ]
    article_authors = [
        context['article'].erudit_object.get_authors(formatted=True)
    ]
    issue = context['issue'].erudit_object.get_volume_numbering(formatted=True)
    issue_url = "https://www.erudit.org{path}".format(
        path=reverse(
            'public:journal:issue_detail',
            kwargs=dict(
                journal_code=context['issue'].journal.code,
                issue_slug=context['issue'].volume_slug,
                localidentifier=context['issue'].localidentifier
            )
        )
    )

    abstracts = [
        context['article'].erudit_object.get_abstracts(formatted=True)[0]['content']
    ]
    article_citation = "Bowen, Dore. « The Diorama Effect: Gas, Politics, and Opera\
     in the 1825 Paris Diorama », Intermédialités : histoire et théorie des arts,\
      des lettres et des techniques / Intermediality: History and Theory of the\
       Arts, Literature and Technologies, n° 24-25, automne 2014, printemps 2015.\
        DOI: 10.7202/1034155ar"
    article_url = "http://id.erudit.org/iderudit/1043218ar"
    article_doi = "http://dx.doi.org/10.7202/1043218ar"

    # Horizontal rules
    fullBlackLine = line('black', 552)
    fullGreyLine = line('#cccccc', 552)

    # Links
    article_link = '<link href="' + article_url + '">' + '→ Consulter l’article en ligne' + '</link>'
    issue_link = '<link href="' + issue_url + '">' + '→ Aller au sommaire du numéro' + '</link>'
    journal_link = '<link href="' + journal_url + '">' + '→ Découvrir la revue' + '</link>'

    # Image dimensions
    erudit_logo.drawHeight = 25
    erudit_logo.drawWidth = 75.75

    # Text styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Heading", fontName="Spectral", fontSize=14, leading=15
    ))
    styles.add(ParagraphStyle(
        name="Small", fontName="Spectral", fontSize=8, leading=10
    ))
    styles.add(ParagraphStyle(
        name="FooterText", fontName="Spectral", fontSize=6, leading=7
    ))
    styles.add(ParagraphStyle(
        name="Subheading", fontName="Spectral", fontSize=10, leading=10
    ))

    # -----------------------------------------------------------------------------
    # HEADER
    # Admin info: PDF creation, institution
    ptext = """
        <font color='grey'>Document généré le %s.
        Accès offert par : %s.</font>
    """ % (date, institution)
    Story.append(Paragraph(ptext, styles["Small"]))

    Story.append(Spacer(0.25, 5))
    Story.append(fullBlackLine)

    # Journal info
    Story.append(Spacer(0.25, 10))
    for title in journal_titles:
        ptext = """
            <font size='10' color='grey'>%s</font>
        """ % (title)
    Story.append(Paragraph(ptext, styles["Subheading"]))

    Story.append(Spacer(0.25, 5))

    # Article titles
    Story.append(Spacer(0.25, 10))
    for title in article_titles:
        ptext = """
            <font>%s</font>
        """ % (title)
        Story.append(Paragraph(ptext, styles["Heading"]))
        Story.append(Spacer(0.25, 7.5))

    # Article authors
    Story.append(Spacer(0.25, 25))
    ptext = "<font size='10'>"
    for author in article_authors:
        ptext = ptext + "%s, " % (author)
    ptext = ptext + "</font>"
    Story.append(Paragraph(ptext, styles["Subheading"]))

    Story.append(Spacer(0.25, 10))
    Story.append(fullGreyLine)
    Story.append(Spacer(0.25, 10))

    # -----------------------------------------------------------------------------
    # BODY

    # Issue info
    left_text = """
        <font size='10'>Numéro</font>
        <br/><br/>
        <font>%s</font>
        <br/><br/>
        <font color='#ff4242'>%s</font>
        <br/><br/><br/>
        <font size='10'>Éditeurs</font>
        <br/><br/>
    """ % (issue, issue_link)

    # Publisher info
    for publisher in journal_publishers:
        left_text = left_text + """
            <font>%s</font>
            <br/><br/>
        """ % (publisher)

    # Journal info
    left_text = left_text + """
        <font color='#ff4242'>%s</font>
        <br/><br/><br/>
    """ % (journal_link)

    # TODO: ISSN

    # How to cite
    left_text = left_text + """
        <font size='10'>Citer cet article</font>
        <br/><br/>
        <font>%s</font>
    """ % (article_citation)

    # Article abstracts
    right_text = """
        <font size='10'>Résumé de l’article</font>
        <br/><br/>
    """

    if abstracts:
        for abstract in abstracts:
            right_text = right_text + """
                <font color='grey'>%s…</font>
                <br/><br/>
            """ % (abstract)
    else:
        right_text = right_text + """
            <font color='grey'>
            [Aucun résumé pour cet article]
            </font>
        """

    right_text = right_text + """
        <font color='#ff4242'>%s</font>
        """ % (article_link)

    # Body table
    issue_info = [(
        Paragraph(left_text, styles["Small"]),
        Paragraph(right_text, styles["Small"])
    )]
    table = Table(
        issue_info,
        colWidths=276,
        rowHeights=350,
    )
    table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    Story.append(table)

    Story.append(Spacer(0.25, 5))

    # -----------------------------------------------------------------------------
    # FOOTER

    # Copyright info
    copyright_text = """
        <font>Lorem ipsum dolor sit amet</font>
        <br/><br/>
    """

    # Legal statement
    statement_text = """
        <font>Ce document est protégé par la loi sur
        le droit d'auteur. L'utilisation des services d'Érudit (y compris la
        reproduction) est assujettie à sa politique d'utilisation que vous
        pouvez consulter en ligne.
        [%s]
        </font>
        <br/><br/>
    """ % (policy_url)

    # Legal information table
    legal_info = [(
        Paragraph(copyright_text, styles["FooterText"]),
        Paragraph(statement_text, styles["FooterText"])
    )]
    table = Table(
        legal_info,
        colWidths=276,
        rowHeights=30,
    )
    table.setStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
    ])

    # Mission statement
    mission_text = """
        <font size='10'>Cet article est diffusé
        et préservé par Érudit.</font>
        <br/><br/>
        <font>Érudit est un consortium
        interuniversitaire sans but lucratif composé de l’Université de Montréal,
        l’Université Laval et l’Université du Québec à Montréal. Il a pour mission
        la promotion et la valorisation de la recherche. [%s]
        </font>
    """ % (erudit_url)

    # Footer table
    erudit_info = [(
        Paragraph(copyright_text, styles["FooterText"]),
        Paragraph(statement_text, styles["FooterText"])),
        (erudit_logo, Paragraph(mission_text, styles["FooterText"]))
    ]
    footer_table = Table(
        erudit_info,
        colWidths=276,
        rowHeights=50,
    )
    footer_table.setStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LINEABOVE", (0, 1), (-1, -1), 0.25, colors.black),
    ])

    def footerContent(canvas, doc):
        canvas.saveState()
        footer = footer_table
        w, h = footer.wrap(276, doc.bottomMargin)
        footer.drawOn(canvas, 35, 15)
        canvas.restoreState()

    # -----------------------------------------------------------------------------
    # BUILD COVERPAGE

    c.build(Story, onFirstPage=footerContent)
    return buf
