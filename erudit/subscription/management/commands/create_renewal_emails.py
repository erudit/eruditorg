import csv

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile, File
from post_office import mail

from subscription.models import Client, Product, RenewalNotice
from subscription import report

class Command(BaseCommand):

    help = """Importe les données de réabonnement depuis Victor

La commande prend un seul paramètre, qui est le chemin vers
le répertoire dans lequel les fichiers CSV générés par Victor
sont stockés.

Le script s'attend à y trouver les fichiers suivants:

* clients.csv
"""

    client_file = [""]

    def handle(self, *args, **options):

        for renewal in RenewalNotice.objects.all():
            report_data = report.generate_report(renewal)
            pdf = ContentFile(report_data)

            mail.send(
                'david@cormier.xyz',
                'david@cormier.xyz',
                attachments={
                    'avis.pdf': pdf
                },
                template='avis_de_renouvellement',
            )
