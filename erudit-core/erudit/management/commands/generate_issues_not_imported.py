# -*- coding: utf-8 -*-
import logging
from django.core.management.base import BaseCommand
from erudit.fedora.utils import get_unimported_issues_pids

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """ Checks if issues in fedora are all in eruditorg database.
        Then generates a list of pid of the missing one
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--display-unpublished', action='store_true', dest='display_unpublished', default=False,
            help='Display unpublished issues.')

    help = 'generate missing issues in database'

    def handle(self, *args, **options):
        self.display_unpublished = options.get('display_unpublished', False)

        unimported_issues = get_unimported_issues_pids()

        nb_missing_issues = len(unimported_issues)
        for unimported_issue_pid in unimported_issues:
            logger.info(unimported_issue_pid)
        logger.info('Total Missing issues: {}'.format(nb_missing_issues))
