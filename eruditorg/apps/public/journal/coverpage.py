import io

from datetime import datetime

from reportlab.lib import colors
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

pdfmetrics.registerFont(TTFont('Maax-Regular', 'https://gitlab.erudit.org/erudit/portail/eruditorg/raw/master/eruditorg/static/fonts/maax/Sans-Regular.ttf'))


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


def get_pdf():
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
    journal_url = "https://www.erudit.org/fr/revues/hstc/"
    journal_publishers = [
        "HSTC Publications",
    ]
    article_titles = [
        "Féminisme sans frontières ?... les défis conceptuels",
        "DUFOUR, Pascale, Dominique MASSON et Dominique CAOUETTE (dir.). 2010. <em>Solidarities Beyond Borders : Transnationalizing Women’s Movements</em>. Vancouver, Toronto, UBC Press",
        "FALQUET, Jules, Helena HIRATA, Danièle KERGOAT, Brahim LABARI, Nicky LE FEUVRE et Fatou SOW (dir.). 2010. <em>Le sexe de la mondialisation : genre, classe, race et nouvelle division du travail</em>. Paris, Presses de Sciences Po",
        "MARQUES-PEREIRA, Bérengère, Petra MEIER et David PATERNOTTE (dir.). 2010. <em>Au-delà et en deçà de l’État : Le genre entre dynamiques transnationales et multi-niveaux</em>. Bruxelles, Academia Bruylant",
    ]
    article_authors = [
        "Bostjan Zupanćić",
        "Elżbieta M. Goździak"
    ]
    issue = "Volume 8, Numéro 2, décembre, December, 1984, p. 160–161"
    issue_url = "https://www.erudit.org/fr/revues/hstc/1984-v8-n2-hstc3217/"
    abstracts = [
        "Lorsque le directeur de La Revue musicale sim, Jules Écorcheville, part pour le front en 1914, il écrit à son ami Émile Vuillermoz :Si je ne reviens pas, je vous recommande notre oeuvre, cher ami. Et surtout, si vous tenez à me faire plaisir dans l’autre monde, efforcez-vous de maintenir la concorde et l’harmonie entre les différents éléments qui vont se trouver en présence à ma disparition. Notre revue est faite de différentes pièces ajustées (Amis, sim, etc.), qui tiennent en équilibre par miracle, quelques années de cohésion sont absolument nécessaires encore et c’est précisément cette concentration de nos différentes forces qu’il faudrait maintenir. En tout cas, il ne faudrait pas que ma disparition entraînât celle d’une oeuvre qui nous a coûté, à tous, tant de peine. N’est-il pas vrai ?…",
        "When the director of La Revue sim, Jules Ecorcheville, left for the front in 1914, he wrote to his friend Émile Vuillermoz:If I do not come back, I recommend our work, dear friend. And above all, if you want to please me in the other world, try to maintain concord and harmony between the various elements that will be in the presence of my disappearance. Our periodical is made of different adjusted pieces (Friends, sim, etc.), which balance by miracle, a few years of cohesion are absolutely necessary again and it is precisely this concentration of our different strengths that should be maintained. In any case, my disappearance should not entailed that of a work which cost us, all, so much trouble. Is not it true?…",
    ]
    article_citation = "Bowen, Dore. « The Diorama Effect: Gas, Politics, and Opera\
     in the 1825 Paris Diorama », Intermédialités : histoire et théorie des arts,\
      des lettres et des techniques / Intermediality: History and Theory of the\
       Arts, Literature and Technologies, n° 24-25, automne 2014, printemps 2015.\
        DOI: 10.7202/1034155ar"
    article_url = "http://id.erudit.org/iderudit/1043218ar"

    # Horizontal rules
    fullBlackLine = line('black', 552)
    fullGreyLine = line('#cccccc', 552)

    # Links
    article_link = '<link href="' + article_url + '">' + 'Consulter l’article en ligne' + '</link>'
    issue_link = '<link href="' + issue_url + '">' + 'Aller au sommaire du numéro' + '</link>'
    journal_link = '<link href="' + journal_url + '">' + 'Découvrir la revue' + '</link>'

    # Image dimensions
    erudit_logo.drawHeight = 25
    erudit_logo.drawWidth = 75.75

    # Text styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Heading", fontSize=14, leading=15))
    styles.add(ParagraphStyle(name="Small", fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="FooterText", fontSize=6, leading=7))


    # -----------------------------------------------------------------------------
    # HEADER
    # Admin info: PDF creation, institution
    ptext = """
        <font name='Maax-Regular' color='grey'>Document généré le %s.
        Accès offert par : %s.</font>
    """ % (date, institution)
    Story.append(Paragraph(ptext, styles["Small"]))

    Story.append(Spacer(0.25, 5))
    Story.append(fullBlackLine)

    # Journal info
    Story.append(Spacer(0.25, 10))
    for title in journal_titles:
        ptext = """
            <font name='Maax-Regular' size='10' color='grey'>%s</font>
        """ % (title)
    Story.append(Paragraph(ptext, styles["Normal"]))

    Story.append(Spacer(0.25, 5))

    # Article titles
    Story.append(Spacer(0.25, 10))
    for title in article_titles:
        ptext = """
            <font name='Maax-Regular'>%s</font>
        """ % (title)
        Story.append(Paragraph(ptext, styles["Heading"]))
        Story.append(Spacer(0.25, 7.5))

    # Article authors
    Story.append(Spacer(0.25, 25))
    ptext = "<font name='Spectral' size='10'>"
    for author in article_authors:
        ptext = ptext + "%s, " % (author)
    ptext = ptext + "</font>"
    Story.append(Paragraph(ptext, styles["Normal"]))

    Story.append(Spacer(0.25, 10))
    Story.append(fullGreyLine)
    Story.append(Spacer(0.25, 10))

    # -----------------------------------------------------------------------------
    # BODY

    # Issue info
    left_text = """
        <font name='Maax-Regular' size='10'>Numéro</font>
        <br/><br/>
        <font name='Maax-Regular'>%s</font>
        <br/><br/>
        <font name='Maax-Regular' color='#ff4242'>%s</font>
        <br/><br/><br/>
        <font name='Maax-Regular' size='10'>Éditeurs</font>
        <br/><br/>
    """ % (issue, issue_link)

    # Publisher info
    for publisher in journal_publishers:
        left_text = left_text + """
            <font name='Maax-Regular'>%s</font>
            <br/><br/>
            <font name='Maax-Regular' color='#ff4242'>%s</font>
            <br/><br/><br/>
        """ % (publisher, journal_link)

    # TODO: ISSN

    # How to cite
    left_text = left_text + """
        <font name='Maax-Regular' size='10'>Citer cet article</font>
        <br/><br/>
        <font name='Maax-Regular'>%s</font>
    """ % (article_citation)

    # Article abstracts
    right_text = """
        <font name='Maax-Regular' size='10'>Résumé de l’article</font>
        <br/><br/>
    """

    if abstracts:
        for abstract in abstracts:
            right_text = right_text + """
                <font name='Spectral' color='grey'>%s</font>
                <br/><br/>
            """ % (abstract)
    else:
        right_text = right_text + """
            <font name='Spectral' color='grey'>
            [Aucun résumé pour cet article]
            </font>
        """

    right_text = right_text + """
        <font name='Maax-Regular' color='#ff4242'>%s</font>
        """ % (article_link)

    # Body table
    issue_info = [
        (Paragraph(left_text, styles["Small"]), Paragraph(right_text, styles["Small"]),)
    ]
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
        <font name='Maax-Regular'>Lorem ipsum dolor sit amet</font>
        <br/><br/>
    """

    # Legal statement
    statement_text = """
        <font name='Maax-Regular'>Ce document est protégé par la loi sur
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
        <font name='Maax-Regular' size='10'>Cet article est diffusé
        et préservé par Érudit.</font>
        <br/><br/>
        <font name='Maax-Regular'>Érudit est un consortium
        interuniversitaire sans but lucratif composé de l’Université de Montréal,
        l’Université Laval et l’Université du Québec à Montréal. Il a pour mission
        la promotion et la valorisation de la recherche. [%s]
        </font>
    """ % (erudit_url)

    # Footer table
    erudit_info = [
        (Paragraph(copyright_text, styles["FooterText"]), Paragraph(statement_text, styles["FooterText"])),
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
