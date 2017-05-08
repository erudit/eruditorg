import logging
from django.core.management.base import BaseCommand
from erudit.models import Issue, Article

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set the accessible attribute on article objects'

    def add_arguments(self, parser):
        parser.add_argument(action='store', dest='issue_id', nargs='*', type=str)

    def handle(self, *args, **options):
        issue_ids = options.get('issue_id', None)
        issues = Issue.objects.filter(journal__collection__code='erudit')
        if issue_ids:
            issues = issues.filter(localidentifier__in=issue_ids)
        for issue in issues:
            if not issue.get_erudit_object():
                logger.warn('No fedora object for {}'.format(
                    issue.localidentifier
                ))
                continue
            non_accessible_articles = [
                accessible.getparent() for accessible in issue.get_erudit_object()._root.xpath(
                    './/article/accessible'
                )
            ]

            article_ids = [
                a.get('idproprio') for a in non_accessible_articles
            ]

            Article.objects.filter(
                localidentifier__in=article_ids
            ).update(
                publication_allowed=False
            )

            for article_id in article_ids:
                logger.info("{} {} {}".format(
                    issue.localidentifier, article_id, False
                ))
