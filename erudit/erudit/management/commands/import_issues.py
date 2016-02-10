import logging

from django.core.management.base import BaseCommand
from erudit.models.core import Journal, Issue

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = """Importissues from edinum"""

    def handle(self, *args, **options):

        for journal in Journal.objects.all():
            try:
                print("=" * 50)
                print("Importing {}".format(journal.localidentifier))
                print("=" * 50)
                journal_xml = journal.get_fedora_object().getObjectXml()
                issues = journal_xml.node.findall('.//numero')
                for issue_xml in issues:
                    domain, journal_pid, issue_pid = issue_xml.get('pid').split('.')
                    try:
                        journal = Journal.objects.get(localidentifier=journal_pid)
                        issue = Issue(
                            journal=journal,
                            localidentifier=issue_pid
                        )
                        fedora_object = issue.get_fedora_object()
                        summary = fedora_object.getDatastreamObject('SUMMARY')
                        issue.year = summary.content.node.find('.//annee').text
                        issue.save()
                        print("Imported {}".format(
                            issue.get_full_identifier()
                        ))
                    except Exception:
                        print("Cannot import {}".format(
                            issue.get_full_identifier()
                        ))

            except Exception:
                log.error('Journal with code "{}" does not exist'.format(
                    journal.localidentifier
                ))
