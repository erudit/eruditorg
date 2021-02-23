from django.core.management.base import BaseCommand, CommandError
from django.test import override_settings
from PyPDF2 import PdfFileReader, PdfFileWriter

from apps.public.journal.coverpage import get_coverpage
from erudit.models import Article


FEDORA_IDS = [
    "erudit:erudit.ae49.ae04480.1058425ar",
    "erudit:erudit.alterstice02303.alterstice03141.1040626ar",
    "erudit:erudit.approchesind0522.approchesind04155.1054332ar",
    "erudit:erudit.arbo139.arbo04278.1055879ar",
    "erudit:erudit.archives02160.archives03112.1040390ar",
    "erudit:erudit.bioethics04274.bioethics04449.1058139ar",
    "erudit:erudit.bl1000329.bl1005371.6625ac",
    "erudit:erudit.bo02111.bo03553.1044260ar",
    "erudit:erudit.cqd27.cqd2435.600855ar",
    "erudit:erudit.crs123.crs04254.1055716ar",
    "erudit:erudit.documentation0784.documentation03466.1043718ar",
    "erudit:erudit.ei50.ei03272.1042058ar",
    "erudit:erudit.espace1041666.espace1049539.8928ac",
    "erudit:erudit.etudfr13.etudfr04244.1055654ar",
    "erudit:erudit.globe134.globe1498639.1000860ar",
    "erudit:erudit.haf18.haf700.007801ar",
    "erudit:erudit.im118.im03868.1049943ar",
    "erudit:erudit.ltp26.ltp3628.039051ar",
    "erudit:erudit.meta15.meta05184.1068212ar",
    "erudit:erudit.meta15.meta1279.013266ar",
    "erudit:erudit.mi115.mi04103.1053682ar",
    "erudit:erudit.mi115.mi04103.1053684ar",
    "erudit:erudit.mlj128.mlj05124.1067517ar",
    "erudit:erudit.mlj128.mlj0816.1018390ar",
    "erudit:erudit.nb1073421.nb04552.90657ac",
    "erudit:erudit.ncre040.ncre04255.1055733ar",
    "erudit:erudit.philoso16.philoso0186.1011608ar",
    "erudit:erudit.rgd01024.rgd04358.1056823ar",
    "erudit:erudit.rql33.rql1022.012248ar",
    "erudit:erudit.rse22.rse04446.1058110ar",
    "erudit:erudit.rseau67.rseau04245.1055592ar",
    "erudit:erudit.rseau67.rseau3275.705195ar",
    "erudit:erudit.scesprit04995.scesprit05130.1067588ar",
    "erudit:erudit.sp02131.sp04852.1064011ar",
    "erudit:erudit.sp02131.sp04857.1064453ar",
    "erudit:erudit.spirale1048177.spirale04246.89625ac",
    "erudit:erudit.uhr100.uhr0896.1019391ar",
]


class Command(BaseCommand):
    help = "Generate multiple PDF coverpages for testing purposes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--additional-id-list",
            action="store",
            dest="additional_id_list",
            help="Use default list of IDs, but add this custom list too.",
        )
        parser.add_argument(
            "--custom-id-list",
            action="store",
            dest="custom_id_list",
            help="Do not use default list of IDs, use this custom list instead.",
        )
        parser.add_argument(
            "-l",
            "--locale",
            action="store",
            dest="locale",
            default="fr",
            help="Locale to use for the coverpage translated strings.",
        )

    def handle(self, *args, **options):
        additional_ids = options.get("additional_id_list")
        custom_ids = options.get("custom_id_list")
        locale = options.get("locale")

        with open("./pdf_coverpages.pdf", "wb") as pdf:
            pdf_writer = PdfFileWriter()

            if additional_ids is not None and custom_ids is not None:
                raise CommandError(
                    "Cannnot use both --additional-id-list and --custom-id-list arguments."
                )  # noqa
            elif additional_ids is not None:
                fedora_ids = FEDORA_IDS + additional_ids.split(",")
            elif custom_ids is not None:
                fedora_ids = custom_ids.split(",")
            else:
                fedora_ids = FEDORA_IDS

            for fedora_id in fedora_ids:
                try:
                    _, journal_code, issue_localidentifier, localidentifier = fedora_id.split(".")
                except ValueError:
                    raise CommandError(
                        'Invalid ID "{}", should be in the form "erudit:<collection_id>.<journal_id>.<issue_id>.<article_id>".'.format(
                            fedora_id
                        )
                    )  # noqa

                try:
                    article = Article.from_fedora_ids(
                        journal_code=journal_code,
                        issue_localidentifier=issue_localidentifier,
                        localidentifier=localidentifier,
                    )
                except Article.DoesNotExist:
                    raise CommandError('Article with ID "{}" does not exist.'.format(fedora_id))

                with override_settings(LANGUAGE_CODE=locale):
                    try:
                        pdf_writer.addPage(PdfFileReader(get_coverpage(article)).getPage(0))
                    except (KeyError, ValueError) as error:
                        raise CommandError('Error with ID "{}": {}'.format(fedora_id, error))

            pdf_writer.write(pdf)
            self.stdout.write(self.style.SUCCESS("Success"))
