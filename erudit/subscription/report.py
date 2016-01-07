from io import BytesIO
import locale

from django.contrib.staticfiles import finders

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus.flowables import Image
from reportlab.platypus.tables import Table, TableStyle
from reportlab.pdfgen import canvas

from subscription.models import Country

from erudit import settings

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()
Title = ""
pageinfo = ""


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 10)
        self.drawRightString(
            183 * mm, 15 * mm,
            "Page %d de %d" % (self._pageNumber, page_count)
        )


def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.restoreState()


def generate_report(renewal):

    try:
        country = Country.objects.get(
            name=renewal.receiving_customer.country
        )
        active_locale = country.locale
    except Country.DoesNotExist:
        active_locale = 'en_US'

    locale.setlocale(locale.LC_MONETARY, active_locale)

    content = BytesIO()
    link = styles["Normal"].clone(name="Link")
    link.textColor = Color(0, 0.39, 0.76)
    # styles.add(link)

    label = styles["Normal"].clone(name="Label")
    label.textColor = colors.grey

    value = styles["Normal"].clone(name="value")
    value.firstLineIndent = 20
    # styles.add(value)

    section_header = styles["Normal"].clone(name="SectionHeader")
    section_header.textColor = colors.grey
    section_header.fontSize = 12
    # styles.add(section_header)

    centered_section_header = styles["Normal"].clone(
        name="CenteredSectionHeader"
    )

    centered_section_header.alignment = TA_CENTER

    centered_label = styles["Normal"].clone(
        name="CenteredLabel"
    )
    centered_label.textColor = colors.grey
    centered_label.alignment = TA_CENTER

    centered_text = styles["Normal"].clone(
        name="CenteredText"
    )

    centered_text.alignment = TA_CENTER

    right_text = styles["Normal"].clone(
        name="RightText"
    )

    right_text.alignment = TA_RIGHT

    # styles.add(centered_section_header)

    def wrap_p(string, style=styles["Normal"]):
        return Paragraph(string, style=style)

    def wrap_value(string):
        return Paragraph(string, style=value)

    def wrap_label(string):
        return Paragraph(string, style=label)

    doc = SimpleDocTemplate(content, pagesize=letter)
    Story = []
    img = Image(
        finders.find("erudit.png"),
        width=4 *
        inch,
        height=1.029 * inch
    )

    address = Table([
        [Paragraph(
            '<b>Avis de renouvellement</b>',
            style=styles['Normal']
        )],
        [Paragraph(
            '<b>Subscription Renewal Notice</b>',
            style=styles['Normal']
        )],
        ['Consortium Érudit'],
        ['Université de Montréal'],
        ['Pavillon 3744 Jean-Brillant, bureau 6500'],
        ['Case postale 6128, succ. Centre-ville'],
        ['Montréal (Québec) CANADA, H3C 3J7'],
        [Paragraph(
            '<a href="mailto:{email}"><u>{email}</u></a>'.format(
                email=settings.RENEWAL_FROM_EMAIL
            ),
            style=link)],
    ], rowHeights=0.20 * inch)

    address.setStyle([
        ('BOX', (0, 0), (-1, -1), 2, colors.lightgrey),
    ])

    header = Table(
        [[img, address]],
    )

    header.setStyle(
        TableStyle([
            ('VALIGN', (0, 0), (1, 0), 'TOP'),
        ])
    )

    Story.append(header)

    Story.append(Spacer(0, 0.25 * inch))

    paying_customer_info = Table([
        [wrap_label("Adressée à / Sent to"),
         wrap_label("Date de l'avis / Notice Date")],
        [
            wrap_value("{} {}".format(
                renewal.paying_customer.firstname,
                renewal.paying_customer.lastname
            )),
            wrap_value("07/10/2015")],
        [wrap_label("No d’identification Érudit / Érudit’s ID Number"),
         wrap_label("Numéro de facture / Invoice Number")],
        [wrap_value(str(renewal.paying_customer.pk)),
         wrap_value(renewal.renewal_number)],
        [wrap_label("Courriel / Email"),
         wrap_label("No de bon de commande / PO Number")],
        [wrap_value(renewal.paying_customer.email),
         wrap_value(renewal.po_number)],
    ])

    Story.append(paying_customer_info)

    receiving_customer_info = Table([
        [wrap_p("<b>Information client / Customer Information</b>",
                style=label)],
        [wrap_label("Client / Customer"),
         wrap_label("No d'identification Érudit / Érudit's ID Number")],
        [
            wrap_value(renewal.receiving_customer.organisation),
            wrap_value(str(renewal.receiving_customer.pk))],
        [wrap_label("Contact client / Customer contact"),
         wrap_label("Courriel client / Customer email")],
        [
            wrap_value(
                "{} {}".format(
                    renewal.receiving_customer.firstname or "",
                    renewal.receiving_customer.lastname or ""
                ),
            ),
            wrap_value(renewal.receiving_customer.email)]
    ])

    Story.append(Spacer(0, 0.25 * inch))

    receiving_customer_info.setStyle([
        ('BOX', (0, 0), (-1, -1), 2, colors.lightgrey),
    ])

    Story.append(receiving_customer_info)

    Story.append(Spacer(0, 0.25 * inch))

    def get_items_header():
        return [
            [wrap_p("<b>Description</b>", style=label), "", ""],
            [
                wrap_label("<i>Item</i>"),
                wrap_label("<i>Titre / Title</i>"),
                ""
            ],
        ]

    def _get_basket_items(basket, item_number):
        items = []
        for item_number, title in enumerate(
                basket.titles.filter(
                    hide_in_renewal_items=False), item_number + 1):
            items.append(
                [item_number, title.title, ""]
            )
        return item_number, items

    def _get_title_items(titles, item_number, has_basket=False):
        items = []

        # If there is a basket before the titles, add an empty line
        # to separate it from the rest.
        if has_basket and titles:
            items.append([
                "",
                "",
                "",
            ])

        for item_number, product in enumerate(
                titles, item_number + 1):

            items.append([
                item_number,
                wrap_p(
                    product.title
                ),
                wrap_p(
                    locale.currency(
                        product.amount,
                        symbol=False,
                    ),
                    style=right_text
                )
            ])

        return item_number, items

    def _get_premium_items(premium, item_number):
        items = []
        if premium:
            items.append(
                [
                    item_number + 1,
                    premium.title,
                    wrap_p(
                        locale.currency(
                            premium.amount,
                            symbol=False,
                        ),
                        style=right_text
                    ),
                    ""
                ],
            )
        return item_number + 1, items

    def get_items(renewal):
        items = []
        basket, titles = renewal.get_items_for_renewal()

        item_number = 0

        if basket:

            item_number, basket_items = _get_basket_items(
                basket, item_number
            )

            item_number, premium_items = _get_premium_items(
                renewal.get_premium(), item_number
            )

            items.extend(
                basket_items
            )

            items.extend(
                premium_items
            )

        else:
            item_number, title_items = _get_title_items(
                titles, item_number
            )

            item_number, premium_items = _get_premium_items(
                renewal.get_premium(), item_number
            )

            items.extend(
                title_items
            )

            items.extend(
                premium_items
            )

        return item_number, items

    def get_items_price(item_number):
        items = []

        basket, titles = renewal.get_items_for_renewal()

        if basket:
            items.append(
                [
                    "",
                    "Prix du panier / Collection price",
                    wrap_p(
                        locale.currency(
                            basket.amount,
                            symbol=False,
                        ),
                        style=right_text
                    ),
                    ""
                ]
            )

        if renewal.rebate:
            items.append(
                [
                    Spacer(0, 0.25 * inch),
                    "Rabais institutionnel",
                    wrap_p(
                        locale.currency(
                            renewal.rebate,
                            symbol=False,
                        ),
                        style=right_text
                    ),
                    ""
                ],
            )

        if basket:
            item_number, title_items = _get_title_items(
                titles, item_number, has_basket=True
            )

            items.extend(
                title_items
            )

        if renewal.raw_amount:
            items.append(
                [
                    Spacer(0, 0.25 * inch),
                    wrap_label("Sous-total"),
                    wrap_p(
                        locale.currency(
                            renewal.raw_amount,
                            symbol=False,
                        ),
                        style=right_text
                    ),
                    ""
                ]
            )

        if renewal.harmonized_tax:
            items.extend([
                [
                    Spacer(0, 0.25 * inch) if not renewal.raw_amount else "",
                    wrap_label("TVH / HST"),
                    wrap_p(
                        locale.currency(
                            renewal.harmonized_tax,
                            symbol=False,
                        ),
                        style=right_text
                    ),
                    ""

                ]
            ])
        else:
            items.extend([
                [
                    Spacer(0, 0.25 * inch) if not renewal.raw_amount else "",
                    wrap_label("TPS / GST"),
                    wrap_p(
                        locale.currency(
                            renewal.federal_tax,
                            symbol=False,
                        ),
                        style=right_text
                    ),
                    ""
                ],
                [
                    "",
                    wrap_label("TVQ / PST"),
                    wrap_p(
                        locale.currency(
                            renewal.provincial_tax,
                            symbol=False,
                        ),
                        style=right_text
                    ),
                    ""
                ],
            ])
        items.extend([
            [
                Spacer(0, 0.25 * inch),
                wrap_label("<b>Total</b>"),
                wrap_p(
                    "<b>{}</b>".format(
                        locale.currency(
                            renewal.net_amount,
                            international=True,
                        ),
                    ),
                    style=right_text
                ),
                ""
            ],
        ])

        return items

    items_data = []
    items_header = get_items_header()
    item_number, items = get_items(renewal)
    items_price = get_items_price(item_number)

    items_data.extend(items_header)
    items_data.extend(items)
    items_data.extend(items_price)

    items = Table(
        items_data,
        repeatRows=2,
        # rowHeights=row_heights,
        colWidths=("10%", "60%", "20%", "10%")
    )

    items.setStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('LINEBELOW', (0, 'splitlast'), (3, 'splitlast'), 2, colors.lightgrey),
        ('LINEABOVE', (0, 'splitfirst'), (3, 'splitfirst'), 3, colors.white),
        ('BOX', (0, 0), (-1, -1), 2, colors.lightgrey),
    ])

    Story.append(items)

    Story.append(Spacer(0, 0.25 * inch))

    payment_instructions = Table([
        [
            wrap_p(
                "<b>Modalités de paiement / Payment instructions</b>",
                style=centered_section_header
            )
        ],
        [
            wrap_p(
                "Par chèque payable à l'ordre du Consortium Érudit, SENC"
            ),
            wrap_p(
                "By cheque payable to the order of the Consortium Érudit, SENC"
            )
        ],
        [wrap_p(
            '<a href="mailto:{email}"><u>{email}</u></a>'.format(
                email=settings.RENEWAL_FROM_EMAIL
            ),
            style=link),
         wrap_p(
             '<a href="mailto:{email}"><u>{email}</u></a>'.format(
                 email=settings.RENEWAL_FROM_EMAIL
             ), style=link)]
    ],
        colWidths=("50%", "50%",)
    )

    payment_instructions.setStyle([
        ('SPAN', (0, 0), (-1, 0)),
        ('BOX', (0, 0), (-1, -1), 2, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])

    Story.append(payment_instructions)

    gst_pst = Table([
        [
            wrap_p("<b>No de TPS / GST No</b>", style=centered_label),
            wrap_p("<b>No de TVQ / PST No</b>", style=centered_label),
        ],
        [
            wrap_p("801663741RT0001", style=centered_text),
            wrap_p("1211883894TQ0001", style=centered_text)
        ],
    ])

    Story.append(Spacer(0, 0.25 * inch))
    Story.append(gst_pst)

    doc.build(Story, onLaterPages=myLaterPages, canvasmaker=NumberedCanvas)
    locale.setlocale(locale.LC_MONETARY, '')
    return content.getvalue()
