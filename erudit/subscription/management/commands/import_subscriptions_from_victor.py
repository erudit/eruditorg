import csv

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from subscription.models import Client, Product, RenewalNotice


class Command(BaseCommand):

    help = """Importe les données de réabonnement depuis Victor

La commande prend un seul paramètre, qui est le chemin vers
le répertoire dans lequel les fichiers CSV générés par Victor
sont stockés.

Le script s'attend à y trouver les fichiers suivants:

    * clients.csv
    * titres.csv
    * paniers.csv
    * avis.csv
    * factureproduits.csv
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

        def load_csv_file_in_model(filename, model, generate_pk=False):
            """ Load the given CSV file in the model

            This function expects a CSV whose columns names are
            the same as the object attributes."""
            with open(path + filename, newline='') as csv_file:
                reader = csv.DictReader(csv_file)

                start = model.objects.count()

                for pk, row in enumerate(reader):
                    if not generate_pk:
                        pk = row['pk']
                    else:
                        pk = pk + start
                    model.objects.update_or_create(
                        pk=pk,
                        defaults=row
                    )

        # import clients
        load_csv_file_in_model("clients.csv", Client)

        Product.objects.all().delete()
        load_csv_file_in_model("titres.csv", Product, generate_pk=True)

        # import basket / products

        load_csv_file_in_model("paniers.csv", Product, generate_pk=True)

        RenewalNotice.objects.all().delete()
        with open(path + "avis.csv", newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            currency_fields = [
                "federal_tax", "provincial_tax",
                "harmonized_tax", "amount_total",
                "net_amount", "raw_amount"
            ]

            for pk, row in enumerate(reader):
                pk = pk + 1

                row['paying_customer'] = Client.objects.get(
                    pk=row['paying_customer']
                )

                row['receiving_customer'] = Client.objects.get(
                    pk=row['receiving_customer']
                )

                if not row['rebate']:
                    row['rebate'] = 0

                for cf in currency_fields:
                    row[cf] = float(row[cf].replace(",", "."))

                try:
                    RenewalNotice.objects.update_or_create(
                        pk=pk,
                        defaults=row
                    )
                except ValidationError:
                    print(row)
                    raise

        with open(path + 'factureproduits.csv') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                notice = RenewalNotice.objects.get(
                    renewal_number=row['renewal_number']
                )

                product = Product.objects.get(code=row['code'])

                notice.products.add(product)
                notice.save()

        with open(path + 'panierstitres.csv') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                if Product.objects.filter(code=row['product_code']).exists():
                    basket = Product.objects.get(
                        code=row['basket_code']
                    )

                    product = Product.objects.get(
                        code=row['product_code']
                    )

                    basket.titles.add(product)
                    basket.save()
