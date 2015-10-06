from io import BytesIO, StringIO

import PIL

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus.flowables import Image
from reportlab.platypus.tables import Table, TableStyle
from reportlab.pdfgen import canvas

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
    content = BytesIO()
    link = styles["Normal"].clone(name="Link")
    link.textColor = Color(0, 0.39, 0.76)
    # styles.add(link)

    label = styles["Normal"].clone(name="Label")
    label.textColor = colors.grey
    # styles.add(label)

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
    # styles.add(centered_section_header)

    def wrap_p(string, style=styles["Normal"]):
        return Paragraph(string, style=style)

    def wrap_value(string):
        return Paragraph(string, style=value)

    def wrap_label(string):
        return Paragraph(string, style=label)

    doc = SimpleDocTemplate(content)
    Story = []
    img = Image(
        "/home/dcormier/erudit/projets/admin/erudit/subscription/static/erudit.png",
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
        [Paragraph('<a href="mailto:erudit-abonnements@umontreal.ca"><u>erudit-abonnements@umontreal.ca</u></a>',
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
        [wrap_value(renewal.paying_customer.erudit_number),
         wrap_value(renewal.renewal_number)],
        [wrap_label("Courriel / Email"),
         wrap_label("No de bon de commande / PO Number")],
        [wrap_value(renewal.paying_customer.email),
         wrap_value(renewal.po_number)],
    ])

    Story.append(paying_customer_info)

    receiving_customer_info = Table([
        [wrap_p("<b>Information client / Customer Information</b>", style=label)],
        [wrap_label("Client / Customer"),
         wrap_label("No d'identification Érudit / Érudit's ID Number")],
        [
            wrap_value(renewal.receiving_customer.organisation),
            wrap_value(renewal.receiving_customer.erudit_number)],
        [wrap_label("Contact client / Customer contact"),
         wrap_label("Courriel client / Customer email")],
        [wrap_value("{} {}".format(
            renewal.receiving_customer.firstname or "",
            renewal.receiving_customer.lastname or ""
        ),),
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
            [wrap_label("<i>Item</i>"), wrap_label("<i>Titre / Title</i>"), ""],
        ]

    def get_items(renewal):
        items = []
        basket = renewal.get_basket()

        if basket:
            items = []
            for item_number, title in enumerate(basket.titles.filter(hide_in_renewal_items=False), 1):
                items.append(
                    [item_number, title.title, ""]
                )
            return items
        else:
            for item_number, product in enumerate(renewal.products.filter(hide_in_renewal_items=False), 1):
                # TODO display description if not in a basket
                items.append([item_number, product.title, product.amount])
            return items

    def get_items_price():
        items = []

        basket = renewal.get_basket()
        if basket:
            items.append(
                [
                    "",
                    "Prix du panier / Collection price",
                    basket.amount
                ]
            )

        rebate_spacer_inserted = False
        if renewal.rebate:
            items.append(
                [
                    Spacer(0, 0.25 * inch),
                    "Rabais institutionnel",
                    renewal.rebate
                ],
            )

        premium = renewal.get_premium()

        if premium:
            first_item = "" if rebate_spacer_inserted else Spacer(0, 0.25 * inch)
            items.append(
                [
                    first_item,
                    premium.title,
                    premium.amount,
                ],
            )

        items.extend([
            [
                Spacer(0, 0.25 * inch),
                wrap_label("TPS / GST"),
                renewal.federal_tax
            ],
            [
                "",
                wrap_label("TVQ / PST"),
                renewal.provincial_tax
            ],
            [Spacer(0, 0.25 * inch), wrap_label("<b>Total, Devise / Currency</b>"), wrap_p("<b>{}</b> {}".format(
                renewal.net_amount,
                renewal.currency,
            ))],
        ])

        return items

    items_data = []
    items_header = get_items_header()
    items = get_items(renewal)
    items_price = get_items_price()

    items_data.extend(items_header)
    items_data.extend(items)
    items_data.extend(items_price)

    nb_rows_header_items = len(items_header) + len(items)

    row_heights = [0.2 * inch] * nb_rows_header_items + [None] * len(items_price)

    items = Table(
        items_data,
        repeatRows=2,
        rowHeights=row_heights,
        colWidths=("10%", "60%", "30%")
    )

    items.setStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('LINEBELOW', (0, 'splitlast'), (2, 'splitlast'), 2, colors.lightgrey),
        ('LINEABOVE', (0, 'splitfirst'), (2, 'splitfirst'), 3, colors.white),
        ('BOX', (0, 0), (-1, -1), 2, colors.lightgrey),
    ])

    Story.append(items)

    Story.append(Spacer(0, 0.25 * inch))

    payment_instructions = Table([
        [wrap_p("<b>Modalités de paiement / Payment instructions</b>", style=centered_section_header)],
        [wrap_p("Par chèque payable à l'ordre du Consortium"), wrap_p("By cheque payable at the order of the Consortium")],
        [wrap_p("Par virement bancaire (ajouter 15$ de frais)"), wrap_p("By bank transfer (add 15$ CAN of fee)")],
        [wrap_p('<a href="mailto:erudit-abonnements@umontreal.ca"><u>erudit-abonnements@umontreal.ca</u></a>', style=link),
         wrap_p('<a href="mailto:erudit-abonnements@umontreal.ca"><u>erudit-abonnements@umontreal.ca</u></a>', style=link)]
    ],
        colWidths=("50%", "50%",)
    )

    payment_instructions.setStyle([
        ('SPAN', (0, 0), (-1, 0)),
        ('BOX', (0, 0), (-1, -1), 2, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])

    Story.append(payment_instructions)

    doc.build(Story, onLaterPages=myLaterPages, canvasmaker=NumberedCanvas)

    return content.getvalue()
