import datetime
import io
import re
import sentry_sdk
import structlog

from arabic_reshaper import reshape
from bidi.algorithm import get_display
from bs4 import BeautifulSoup, Tag
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext as _, get_language
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.pdfdoc import PDFString
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Image, KeepInFrame, Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus.tables import Table, TableStyle
from urllib.parse import urlparse

from erudit.models.journal import Article
from erudit.fedora.cache import get_cached_datastream_content

logger = structlog.get_logger()

STATIC_ROOT = str(Path(__file__).parents[3] / "static")
FONTS_DIR = str(Path(STATIC_ROOT) / "fonts")

# NotoSerif font
registerFont(TTFont("NotoSerif", FONTS_DIR + "/Noto/NotoSerif-Regular.ttf"))
registerFont(TTFont("NotoSerif-Bold", FONTS_DIR + "/Noto/NotoSerif-Bold.ttf"))
registerFont(TTFont("NotoSerif-Italic", FONTS_DIR + "/Noto/NotoSerif-Italic.ttf"))
registerFont(TTFont("NotoSerif-BoldItalic", FONTS_DIR + "/Noto/NotoSerif-BoldItalic.ttf"))
registerFontFamily(
    "NotoSerif",
    normal="NotoSerif",
    bold="NotoSerif-Bold",
    italic="NotoSerif-Italic",
    boldItalic="NotoSerif-BoldItalic",
)
addMapping("NotoSerif", 0, 0, "NotoSerif")
addMapping("NotoSerif-Bold", 1, 0, "NotoSerif Bold")
addMapping("NotoSerif-Italic", 0, 1, "NotoSerif Italic")
addMapping("NotoSerif-BoldItalic", 1, 1, "NotoSerif Bold Italic")

# SpectralSC font (small caps)
registerFont(TTFont("SpectralSC", FONTS_DIR + "/Spectral/SpectralSC-Regular.ttf"))
registerFont(TTFont("SpectralSC-Bold", FONTS_DIR + "/Spectral/SpectralSC-Bold.ttf"))
registerFont(TTFont("SpectralSC-Italic", FONTS_DIR + "/Spectral/SpectralSC-Italic.ttf"))
registerFont(TTFont("SpectralSC-BoldItalic", FONTS_DIR + "/Spectral/SpectralSC-BoldItalic.ttf"))
registerFontFamily(
    "SpectralSC",
    normal="SpectralSC",
    bold="SpectralSC-Bold",
    italic="SpectralSC-Italic",
    boldItalic="SpectralSC-BoldItalic",
)
addMapping("SpectralSC", 0, 0, "SpectralSC")
addMapping("SpectralSC-Bold", 1, 0, "SpectralSC Bold")
addMapping("SpectralSC-Italic", 0, 1, "SpectralSC Italic")
addMapping("SpectralSC-BoldItalic", 1, 1, "SpectralSC Bold Italic")

# Symbola font (emojis)
registerFont(TTFont("Symbola", FONTS_DIR + "/Symbola/Symbola.ttf"))
registerFontFamily("Symbola", normal="Symbola")
addMapping("Symbola", 0, 0, "Symbola")

# NotoSerifCJK font (chinese, japanese, korean)
registerFont(TTFont("NotoSerifCJKsc", FONTS_DIR + "/Noto/NotoSerifCJKsc-Regular.ttf"))
registerFont(TTFont("NotoSerifCJKsc-Bold", FONTS_DIR + "/Noto/NotoSerifCJKsc-Bold.ttf"))
registerFont(TTFont("NotoSerifCJKsc-Italic", FONTS_DIR + "/Noto/NotoSerifCJKsc-Regular.ttf"))
registerFont(TTFont("NotoSerifCJKsc-BoldItalic", FONTS_DIR + "/Noto/NotoSerifCJKsc-Bold.ttf"))
registerFontFamily(
    "NotoSerifCJKsc",
    normal="NotoSerifCJKsc",
    bold="NotoSerifCJKsc-Bold",
    italic="NotoSerifCJKsc-Italic",
    boldItalic="NotoSerifCJKsc-BoldItalic",
)
addMapping("NotoSerifCJKsc", 0, 0, "NotoSerifCJKsc")
addMapping("NotoSerifCJKsc-Bold", 1, 0, "NotoSerifCJKsc Bold")
addMapping("NotoSerifCJKsc-Italic", 0, 1, "NotoSerifCJKsc Italic")
addMapping("NotoSerifCJKsc-BoldItalic", 1, 1, "NotoSerifCJKsc Bold Italic")

# NotoSansCanadianAboriginal font
registerFont(
    TTFont(
        "NotoSansCanadianAboriginal",
        FONTS_DIR + "/Noto/NotoSansCanadianAboriginal-Regular.ttf",
    )
)
registerFontFamily("NotoSansCanadianAboriginal", normal="NotoSansCanadianAboriginal")
addMapping("NotoSansCanadianAboriginal", 0, 0, "NotoSansCanadianAboriginal")

# Amiri font (arabic)
registerFont(TTFont("Amiri", FONTS_DIR + "/Amiri/Amiri-Regular.ttf"))
registerFont(TTFont("Amiri-Bold", FONTS_DIR + "/Amiri/Amiri-Bold.ttf"))
registerFont(TTFont("Amiri-Italic", FONTS_DIR + "/Amiri/Amiri-Slanted.ttf"))
registerFont(TTFont("Amiri-BoldItalic", FONTS_DIR + "/Amiri/Amiri-BoldSlanted.ttf"))
registerFontFamily(
    "Amiri",
    normal="Amiri",
    bold="Amiri-Bold",
    italic="Amiri-Italic",
    boldItalic="Amiri-BoldItalic",
)
addMapping("Amiri", 0, 0, "Amiri")
addMapping("Amiri-Bold", 1, 0, "Amiri Bold")
addMapping("Amiri-Italic", 0, 1, "Amiri Italic")
addMapping("Amiri-BoldItalic", 1, 1, "Amiri Bold Italic")

# Dicts of supported characters in our fonts.
noto_chars = TTFont("NotoSerif", FONTS_DIR + "/Noto/NotoSerif-Regular.ttf").face.charWidths
cjk_chars = TTFont("NotoSerifCJKsc", FONTS_DIR + "/Noto/NotoSerifCJKsc-Regular.ttf").face.charWidths
symbola_chars = TTFont("Symbola", FONTS_DIR + "/Symbola/Symbola.ttf").face.charWidths
aboriginal_chars = TTFont(
    "NotoSansCanadianAboriginal",
    FONTS_DIR + "/Noto/NotoSansCanadianAboriginal-Regular.ttf",
).face.charWidths
arabic_chars = TTFont("Amiri", FONTS_DIR + "/Amiri/Amiri-Regular.ttf").face.charWidths


def get_coverpage(article: Article) -> io.BytesIO:
    pdf_buffer = io.BytesIO()

    template = SimpleDocTemplate(
        pdf_buffer,
        # Letter size: 612 points by 792 points
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
        title=PDFString(article.title, enc="raw"),
        author=PDFString(article.get_formatted_authors_without_suffixes(), enc="raw"),
        creator="Érudit",
        subject="",
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
    styles = get_stylesheet(article.erudit_object.language)

    # Text.
    story = []

    # -----------------------------------------------------------------------------
    # INFO

    # PDF creation date & time.
    story.append(
        Paragraph(
            _("Document généré le %(now_dt)s")
            % {
                "now_dt": formats.date_format(
                    datetime.datetime.now(tz=timezone.get_current_timezone()),
                    "SHORT_DATETIME_FORMAT",
                ),
            },
            styles["small_grey"],
        )
    )

    # Black line.
    story.append(medium_spacer)
    story.append(black_line)
    story.append(medium_spacer)

    # -----------------------------------------------------------------------------
    # HEADER

    header = []

    # Journal main title.
    journal_titles = article.issue.erudit_object.get_journal_title()
    journal_main_title = journal_titles.get("main")
    header.append(
        Paragraph(
            journal_main_title.title,
            styles["h3"],
        )
    )
    # Journal main subtitle.
    if journal_main_title.subtitle:
        header.append(
            Paragraph(
                journal_main_title.subtitle,
                styles["h4"],
            )
        )

    # Journal parallel titles.
    for journal_paral_title in journal_titles.get("paral"):
        if journal_main_title.title != journal_paral_title.title:
            header.append(small_spacer)
            header.append(
                Paragraph(
                    journal_paral_title.title,
                    styles["h3"],
                )
            )
        # Journal parallel subtitles.
        if journal_paral_title.subtitle:
            header.append(
                Paragraph(
                    journal_paral_title.subtitle,
                    styles["h4"],
                )
            )
    header.append(extra_large_spacer)

    # Article titles.
    titles = article.erudit_object.get_titles()
    if titles["main"].title is None and not titles["reviewed_works"]:
        header.append(
            Paragraph(
                _("[Article sans titre]"),
                styles["h1"],
            )
        )
    if titles["main"].title:
        header.append(
            Paragraph(
                clean(titles["main"].title, article=article, font_weight="bold"),
                styles["h1"],
            )
        )
        if titles["main"].subtitle:
            header.append(
                Paragraph(
                    clean(titles["main"].subtitle, article=article, font_weight="bold"),
                    styles["h1_grey"],
                )
            )
        for title in titles["paral"] + titles["equivalent"]:
            header.append(small_spacer)
            header.append(
                Paragraph(
                    clean(title.title, article=article, font_weight="bold"),
                    styles["h1"] if title.subtitle else styles["h1_grey"],
                )
            )
            if title.subtitle:
                header.append(
                    Paragraph(
                        clean(title.subtitle, article=article, font_weight="bold"),
                        styles["h1_grey"],
                    )
                )
    for title in titles["reviewed_works"]:
        header.append(small_spacer)
        header.append(
            Paragraph(
                clean(title, article=article, font_weight="bold"),
                styles["h1_grey"],
            )
        )
    header.append(large_spacer)

    # Article authors.
    header.append(
        Paragraph(
            clean(article.get_formatted_authors_without_suffixes(), article=article),
            styles["h2"],
        )
    )

    # Journal path.
    journal_path = reverse(
        "public:journal:journal_detail",
        kwargs={
            "code": article.issue.journal.code,
        },
    )
    # Journal logo.
    journal_logo_ds = get_cached_datastream_content(
        article.issue.journal.get_full_identifier(),
        "LOGO",
    )
    if journal_logo_ds is not None:
        journal_logo = HyperlinkedImage(
            io.BytesIO(journal_logo_ds),
            hyperlink="https://www.erudit.org{}".format(journal_path),
        )
        # Resize journal logo if it's wider than 80 points.
        journal_logo._restrictSize(80, 220)
    else:
        journal_logo = []
    header_table = Table(
        [(KeepInFrame(472, 220, header), journal_logo)],
        colWidths=(462, 90),
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
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
    themes = article.issue.erudit_object.get_themes(formatted=True, html=True)
    if themes:
        for index, theme in enumerate(themes[0]["names"]):
            left_column.append(
                Paragraph(
                    clean(theme, article=article),
                    styles["normal"] if index == 0 else styles["normal_grey"],
                )
            )
        left_column.append(small_spacer)

    # Volume title.
    left_column.append(
        Paragraph(
            article.issue.volume_title,
            styles["normal"],
        )
    )
    left_column.append(large_spacer)

    # URI & DOI.
    left_column.append(
        Paragraph(
            '{label} <link href="{url}" color="#ff4242">{url}</link>'.format(
                label=_("URI&nbsp;:"),
                url="https://id.erudit.org/iderudit/{path}".format(path=article.localidentifier),
            ),
            styles["normal"],
        )
    )
    if article.doi:
        left_column.append(
            Paragraph(
                '{label} <link href="{url}" color="#ff4242">{url}</link>'.format(
                    label=_("DOI&nbsp;:"),
                    url=article.url_doi,
                ),
                styles["normal"],
            )
        )
    left_column.append(large_spacer)

    # Issue summary link.
    issue_path = reverse(
        "public:journal:issue_detail",
        kwargs={
            "journal_code": article.issue.journal.code,
            "issue_slug": article.issue.volume_slug,
            "localidentifier": article.issue.localidentifier,
        },
    )
    left_column.append(
        Paragraph(
            '<link href="{url}" color="#ff4242">{text}</link>'.format(
                url="https://www.erudit.org{}".format(issue_path),
                text=_("Aller au sommaire du numéro"),
            ),
            styles["normal"],
        )
    )

    # Grey line.
    left_column.append(large_spacer)
    left_column.append(grey_half_line)
    left_column.append(large_spacer)

    # Publishers.
    left_column.append(
        Paragraph(
            _("Éditeur(s)"),
            styles["normal"],
        )
    )
    left_column.append(medium_spacer)
    for publisher in article.erudit_object.publishers:
        left_column.append(
            Paragraph(
                publisher,
                styles["small"],
            )
        )
    left_column.append(large_spacer)

    # ISSN
    if article.issue.erudit_object.issn or article.issue.erudit_object.issn_num:
        left_column.append(
            Paragraph(
                _("ISSN"),
                styles["normal"],
            )
        )
    left_column.append(medium_spacer)
    if article.issue.erudit_object.issn:
        left_column.append(
            Paragraph(
                "{issn} ({label})".format(
                    issn=article.issue.erudit_object.issn,
                    label=_("imprimé"),
                ),
                styles["small"],
            )
        )
    if article.issue.erudit_object.issn_num:
        left_column.append(
            Paragraph(
                "{issn} ({label})".format(
                    issn=article.issue.erudit_object.issn_num,
                    label=_("numérique"),
                ),
                styles["small"],
            )
        )
    left_column.append(large_spacer)

    # Journal link.
    left_column.append(
        Paragraph(
            '<link href="{url}" color="#ff4242">{text}</link>'.format(
                url="https://www.erudit.org{}".format(journal_path),
                text=_("Découvrir la revue"),
            ),
            styles["normal"],
        )
    )

    # Grey line.
    left_column.append(large_spacer)
    left_column.append(grey_half_line)
    left_column.append(large_spacer)

    cite_strings = {
        Article.ARTICLE_DEFAULT: _("Citer cet article"),
        Article.ARTICLE_REPORT: _("Citer ce compte rendu"),
        Article.ARTICLE_OTHER: _("Citer ce document"),
        Article.ARTICLE_NOTE: _("Citer cette note"),
    }

    # Cite this article.
    left_column.append(
        Paragraph(
            cite_strings.get(article.type),
            styles["normal"],
        )
    )
    left_column.append(medium_spacer)
    left_column.append(
        Paragraph(
            clean(article.cite_string_apa, article=article),
            styles["small"],
        )
    )

    # Right column.
    right_column = []

    # Abstracts.
    if article.html_abstract:
        right_column.append(
            Paragraph(
                _("Résumé de l'article"),
                styles["normal"],
            )
        )
        right_column.append(medium_spacer)
        soup = BeautifulSoup(article.html_abstract, features="html.parser")
        for paragraph in soup.find_all("p"):
            right_column.append(
                Paragraph(
                    clean(paragraph, article=article),
                    styles["small"],
                )
            )
            right_column.append(small_spacer)

    # Body table.
    body_table = Table(
        [(KeepInFrame(276, 350, left_column), KeepInFrame(276, 350, right_column))],
        colWidths=276,
        rowHeights=350,
    )
    body_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(body_table)

    # -----------------------------------------------------------------------------
    # FOOTER

    # Copyrights.
    copyrights = []
    copyrights.append(small_spacer)
    for copyright in article.copyrights:
        if "text" in copyright:
            copyrights.append(
                Paragraph(
                    copyright["text"],
                    styles["small"],
                )
            )
            copyrights.append(small_spacer)
        elif "href" in copyright and "img" in copyright:
            try:
                parsed = urlparse(copyright["img"])
                path = STATIC_ROOT + "/img/licensebuttons.net/" + parsed.path
                image = HyperlinkedImage(path, hyperlink=copyright["href"])
                # Resize license logo if it's wider than 50 points.
                image._restrictSize(50, 35)
                copyrights.append(image)
                copyrights.append(small_spacer)
            except OSError:
                pass
    copyrights = KeepInFrame(271, 55, copyrights)

    # Policy.
    policy_urls = {
        "fr": "https://apropos.erudit.org/fr/usagers/politique-dutilisation/",
        "en": "https://apropos.erudit.org/en/users/policy-on-use/",
    }
    statement = []
    statement.append(small_spacer)
    statement.append(
        Paragraph(
            _(
                "Ce document est protégé par la loi sur le droit d’auteur. L’utilisation des services \
        d’Érudit (y compris la reproduction) est assujettie à sa politique d’utilisation que vous \
        pouvez consulter en ligne."
            ),
            styles["small"],
        )
    )
    statement.append(small_spacer)
    statement.append(
        Paragraph(
            '<link href="{url}" color="#ff4242">{url}</link>'.format(url=policy_urls[language]),
            styles["small"],
        )
    )
    statement.append(small_spacer)

    # Mission.
    mission = []
    mission.append(small_spacer)
    mission.append(
        Paragraph(
            _("Cet article est diffusé et préservé par Érudit."),
            styles["small"],
        )
    )
    mission.append(small_spacer)
    mission.append(
        Paragraph(
            _(
                "Érudit est un consortium interuniversitaire sans but lucratif composé de l’Université de \
        Montréal, l’Université Laval et l’Université du Québec à Montréal. Il a pour mission la \
        promotion et la valorisation de la recherche."
            ),
            styles["small_grey"],
        )
    )
    mission.append(small_spacer)
    mission.append(
        Paragraph(
            '<link href="{url}" color="#ff4242">{url}</link>'.format(
                url="https://www.erudit.org/{lang}/".format(lang=language)
            ),
            styles["small"],
        )
    )
    mission.append(small_spacer)

    # Logo.
    logo = []
    logo.append(small_spacer)
    logo.append(
        HyperlinkedImage(
            STATIC_ROOT + "/img/logo-erudit.png",
            hyperlink="https://www.erudit.org/{lang}/".format(lang=language),
            width=75.75,
            height=25,
        )
    )
    logo.append(small_spacer)

    # Footer table
    footer_table = Table(
        [(copyrights, statement), (logo, mission)],
        colWidths=271,
        rowHeights=55,
    )
    footer_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEABOVE", (0, 0), (-1, 0), 1, colors.lightgrey),
                ("LINEABOVE", (0, 1), (-1, -1), 1, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    def footer_content(canvas, document):
        canvas.saveState()
        footer_table.wrap(271, document.bottomMargin)
        footer_table.drawOn(canvas, 35, 15)
        canvas.restoreState()

    # -----------------------------------------------------------------------------
    # BUILD COVERPAGE

    template.build(story, onFirstPage=footer_content)
    return pdf_buffer


def get_stylesheet(language):
    font_name = "NotoSerifCJKsc" if language in ["zh", "ja", "ko"] else "NotoSerif"
    stylesheet = StyleSheet1()
    stylesheet.add(
        ParagraphStyle(
            name="normal",
            fontName=font_name,
            fontSize=8,
            leading=10,
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="bold",
            parent=stylesheet["normal"],
            fontName=f"{font_name}-Bold",
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="italic",
            parent=stylesheet["normal"],
            fontName=f"{font_name}-Italic",
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="bold_italic",
            parent=stylesheet["normal"],
            fontName=f"{font_name}-BoldItalic",
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="h1",
            parent=stylesheet["bold"],
            fontSize=14,
            leading=16,
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="h2",
            parent=stylesheet["normal"],
            fontSize=12,
            leading=14,
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="h3",
            parent=stylesheet["bold"],
            fontSize=12,
            leading=14,
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="h4",
            parent=stylesheet["bold"],
            fontSize=10,
            leading=12,
            textColor=colors.grey,
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="small",
            parent=stylesheet["normal"],
            fontSize=7,
            leading=9,
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="small_grey",
            parent=stylesheet["small"],
            textColor=colors.grey,
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="h1_grey",
            parent=stylesheet["h1"],
            textColor=colors.grey,
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name="normal_grey",
            parent=stylesheet["normal"],
            textColor=colors.grey,
        )
    )
    return stylesheet


def clean(text, article, font_weight=None):
    soup = text if isinstance(text, Tag) else BeautifulSoup(text, "html.parser")
    # Replace <span class="barre"> by <strike>
    for node in soup.find_all("span", attrs={"class": "barre"}):
        del node["class"]
        node.name = "strike"
    # Replace <span class="souligne"> by <u>
    for node in soup.find_all("span", attrs={"class": "souligne"}):
        del node["class"]
        node.name = "u"
    # Uppercase <span class="majuscule"> nodes.
    for node in soup.find_all("span", attrs={"class": "majuscule"}):
        del node["class"]
        node.replace_with(node.text.upper())
    # Change the font of <span class="petitecap"> nodes.
    for node in soup.find_all("span", attrs={"class": "petitecap"}):
        del node["class"]
        node["fontName"] = "SpectralSC-Bold" if font_weight == "bold" else "SpectralSC"
    # Remove any footnotes.
    for node in soup.find_all("a", attrs={"class": "norenvoi"}):
        node.decompose()
    # Remove all other classes we can't transform.
    for node in soup.find_all("span", attrs={"class": re.compile(".*")}):
        del node["class"]
    text = str(soup)

    # Remove unicode variation selectors, they are not supported by our fonts.
    text = re.sub(r"[\uFE00-\uFE0F]", "", text)

    # Check if we have unsupported characters in Noto font.
    text_chars = {ord(c) for c in text}
    chars_not_in_noto = text_chars.difference(set(noto_chars.keys()))
    # If we have unsupported characters, check if they are supported by our other fonts.
    if chars_not_in_noto:
        is_arabic = False
        unsupported_characters = []
        for char in chars_not_in_noto:
            if char in cjk_chars:
                char = chr(char)
                font_name = "NotoSerifCJKsc-Bold" if font_weight == "bold" else "NotoSerifCJKsc"
                text = text.replace(char, f'<span fontName="{font_name}">{char}</span>')
            elif char in symbola_chars:
                char = chr(char)
                text = text.replace(char, f'<span fontName="Symbola">{char}</span>')
            elif char in aboriginal_chars:
                char = chr(char)
                text = text.replace(
                    char,
                    f'<span fontName="NotoSansCanadianAboriginal">{char}</span>',
                )
            elif char in arabic_chars:
                # We can't set font on each character because the reshaping of arabic characters
                # based on their neighbours won't work. See below where we set the Amiri font and we
                # reshape characters and inverse display right to left when `is_arabic` is True.
                is_arabic = True
            else:
                unsupported_characters.append(chr(char))

        if unsupported_characters:
            article_pid = article.get_full_identifier()
            with sentry_sdk.configure_scope() as scope:
                scope.fingerprint = [article_pid]
            # If some characters are not supported by our fonts, log them.
            logger.warning(
                "Coverpage: Unsupported characters",
                unsupported_characters=unsupported_characters,
                article_pid=article_pid,
            )

        # If we have arabic characters, we need to display it right to left (`get_display()`),
        # reshape characters based on their neighbours (`reshape()`) and set the Amiri font.
        if is_arabic:
            font_name = "Amiri-Bold" if font_weight == "bold" else "Amiri"
            text = get_display(reshape(f'<span fontName="{font_name}">{text}</span>'))

    return text


class Line(Flowable):
    def __init__(self, color, width, height):
        Flowable.__init__(self)
        self.color = color
        self.width = width
        self.height = height

    def __repr__(self):
        return f"Line(color={self.color}, width={self.width}, height={self.height})"

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.line(0, self.height, self.width, 0)


class HyperlinkedImage(Image):
    def __init__(
        self,
        filename,
        width=None,
        height=None,
        kind="direct",
        mask="auto",
        lazy=1,
        hAlign="LEFT",
        hyperlink=None,
    ):
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
