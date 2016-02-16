import logging

from django.core.management.base import BaseCommand
from erudit.models.core import Journal, Issue, Article

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
                        volume = summary.content.node.find('.//numero/volume')
                        if volume is not None:
                            issue.volume = volume.text

                        number = summary.content.node.find('.//nonumero')
                        if number is not None:
                            issue.number = number.text
                        issue.title = summary.content.node.find('.//liminaire//titre').text

                        date_produced = summary.content.node.find('.//originator')

                        date_published = summary.content.node.find('.//pubnum/date')
                        if date_published is not None:
                            issue.date_published = date_published.text
                        if date_produced is not None:
                            issue.date_produced = date_produced.get('date')
                        elif date_published is not None:
                            issue.date_produced = date_published.text

                        issue.save()
                        print("Imported {}".format(
                            issue.get_full_identifier()
                        ))

                        for article_xml in summary.content.node.findall('.//article'):

                            id_article = article_xml.get('idproprio')
                            processing = article_xml.get('qualtraitement')

                            if processing == 'minimal':
                                processing = 'M'
                            elif processing == 'complet':
                                processing = 'C'
                            elif processing == '':
                                processing = 'M'
                            else:
                                raise ValueError()

                            article = Article(
                                issue=issue,
                                localidentifier=id_article,
                                processing=processing,
                            )

                            title = article_xml.find('.//liminaire//titre')

                            if title is not None:
                                article.title = title.text
                            surtitle = article_xml.find('.//liminaire//surtitre')
                            if surtitle is not None:
                                article.surtitle = surtitle.text

                            article.save()
                            print("* Imported {}".format(
                                article.get_full_identifier()
                            ))

                    except Exception as e:
                        print("Cannot import {}: {}".format(
                            issue.get_full_identifier(),
                            e
                        ))

            except Exception:
                log.error('Journal with code "{}" does not exist'.format(
                    journal.localidentifier
                ))
