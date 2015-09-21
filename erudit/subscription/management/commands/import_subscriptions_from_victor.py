import csv

from django.core.management.base import BaseCommand, CommandError
from subscription.models import Client, Product, RenewalNotice


class Command(BaseCommand):

    help = """Importe les données de réabonnement depuis Victor

La commande prend un seul paramètre, qui est le chemin vers
le répertoire dans lequel les fichiers CSV générés par Victor
sont stockés.

Le script s'attend à y trouver les fichiers suivants:

    * clients.csv
    """

    client_file = [""]

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):

        if 'path' not in options:
            raise CommandError("You must specify the path")

        path = options['path']

        if not path.endswith("/"):
            path = path + "/"

        def load_csv_file_in_model(filename, model):
            """ Load the given CSV file in the model

            This function expects a CSV whose columns names are
            the same as the object attributes."""
            with open(path + filename, newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    model.objects.update_or_create(
                        pk=row['pk'],
                        defaults=row
                    )

        # import clients
        load_csv_file_in_model("clients.csv", Client)

        load_csv_file_in_model("titres.csv", Product)

        load_csv_file_in_model("paniers.csv", Product)

        with open(path + "avis.csv", newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                row['paying_customer'] = Client.objects.get(
                    pk=row['paying_customer']
                )

                row['receiving_customer'] = Client.objects.get(
                    pk=row['receiving_customer']
                )

                RenewalNotice.objects.update_or_create(
                    pk=row['pk'],
                    defaults=row
                )

        with open(path + 'factureproduits.csv') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                notice = RenewalNotice.objects.get(pk=row['avis_pk'])
                product = Product.objects.get(pk=row['product_pk'])
                notice.products.add(product)
                notice.save()
