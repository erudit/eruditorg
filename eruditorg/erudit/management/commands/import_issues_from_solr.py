# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse
from django.core.management.base import BaseCommand
from django.conf import settings
from erudit.models import Issue
from erudit.models import Journal
import pysolr
import structlog
logger = structlog.getLogger(__name__)


class Command(BaseCommand):
    """ Check if the issues from solr are in the eruditorg
        database (from the specified year until today),
        import the issues that are missing.
    """

    help = 'Import Cairn Issues from Solr'

    def add_arguments(self, parser):
        parser.add_argument(
            '--journal-localidentifier',
            action='store',
            dest='journal_localidentifier',
            default=False,
            help='Journal Localidentifier')

        parser.add_argument(
            '--journal-cairn-code',
            action='store',
            dest='journal_cairn_code',
            default=False,
            help='Journal Cairn Code')

        parser.add_argument(
            '--year-min',
            action='store',
            dest='year_min',
            default=False,
            help='Year from which we look for the issues in solr')

    def handle(self, *args, **options):
        logger.info("import.started", **options)

        for option in options:
            assert option is not None

        self.client = pysolr.Solr(settings.SOLR_ROOT, timeout=settings.SOLR_TIMEOUT)
        self.journal_localidentifier = options.get('journal_localidentifier', None)
        self.year_min = options.get('year_min', None)
        self.year_max = datetime.now().year
        self.journal_cairn_code = options.get('journal_cairn_code', None)
        self.cairn_url = "https://www.cairn.info/numero.php?ID_REVUE={}&ID_NUMPUBLIE="\
            .format(self.journal_cairn_code)
        self.query = 'RevueID:{} AND Annee:[{} TO {}]'\
            .format(
                self.journal_localidentifier,
                self.year_min,
                self.year_max
            )
        self.solr_args = {
            'q': self.query,
            'fl': 'NumeroID, Annee, Volume, Numero, DateAjoutErudit, Periode',
            'sort': 'AnneePublication desc',
            'group': 'true',
            'group.field': 'NumeroID',
            'group.main': 'true',
            'indent': 'true',
            'wt': 'json',
            'rows': '99999',
            'facet.limit': '0',
        }
        self.solr_results = self.client.search(**self.solr_args)
        logger.info(
            "import.started",
            issues_count=len(self.solr_results),
            msg="importing issues found"
        )
        try:
            journal = Journal.objects.get(localidentifier=self.journal_localidentifier)
        except Journal.DoesNotExist:
            logger.error(
                "journal.import.error",
                msg="Journal does not exist",
                journal_localidentifier=self.journal_localidentifier
            )
            return
        for value in self.solr_results:
            issue_year_solr = value['Annee'][0]
            issue_number_solr = '-'.join(value['Numero'])
            date_published = parse(value['DateAjoutErudit']).strftime('%Y-%m-%d')
            issue_localidentifier = value['NumeroID']
            external_url = self.cairn_url + issue_localidentifier
            if 'Periode' in value:
                publication_period = '-'.join(value['Periode']) + ' ' + issue_year_solr
            else:
                publication_period = issue_year_solr
            if 'Volume' in value:
                issue_volume_solr = '-'.join(value['Volume'])
            else:
                issue_volume_solr = None

            issue, created = Issue.objects.get_or_create(
                journal_id=journal.id,
                year=issue_year_solr,
                number=issue_number_solr,
                defaults={
                    'localidentifier': issue_localidentifier,
                    'external_url': external_url,
                    'date_published': date_published,
                    'publication_period': publication_period,
                    'volume': issue_volume_solr,
                    'is_published': 1
                },
            )
            if created:
                logger.info(
                    "issue.imported",
                    msg="importing issue found in solr but not in database",
                    journal=self.journal_localidentifier,
                    year=issue_year_solr,
                    number=issue_number_solr,
                    localidentifier=issue_localidentifier,
                    external_url=external_url,
                    date_published=date_published
                )
            else:
                logger.debug(
                    "import.info",
                    msg="Issue found in solr and in database",
                    journal=self.journal_localidentifier,
                    year=issue.year,
                    number=issue.number,
                    localidentifier=issue.localidentifier,
                    external_url=issue.localidentifier,
                    date_published=issue.date_published
                )
