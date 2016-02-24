import logging

from django.core.management.base import BaseCommand
from erudit.models.core import Author, Journal, Issue, Article

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = """Importissues from edinum"""

    def handle(self, *args, **options):

        for journal in Journal.objects.all():
            self.import_journal(journal)

    def import_journal(self, journal):
        try:
            print("=" * 50)
            print("Importing {}".format(journal.localidentifier))
            print("=" * 50)
            journal_object = journal.get_fedora_object()

            publications = journal_object.getDatastreamObject('PUBLICATIONS')

            issues = publications.content.node.findall('.//numero')

            for issue_xml in issues:
                self.import_issue(issue_xml)

        except Exception:
            log.error('Journal with code "{}" does not exist'.format(
                journal.localidentifier
            ))

    def import_issue(self, issue_xml):
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

                for author_xml in article_xml.findall('.//liminaire//grauteur//auteur'):
                    firstname_xml = author_xml.find('.//nompers/prenom')
                    firstname = firstname_xml.text if firstname_xml is not None else None
                    lastname_xml = author_xml.find('.//nompers/nomfamille')
                    lastname = lastname_xml.text if lastname_xml is not None else None
                    suffix_xml = author_xml.find('.//nompers/suffixe')
                    suffix = suffix_xml.text if suffix_xml is not None else None

                    author, dummy = Author.objects.get_or_create(
                        firstname=firstname, lastname=lastname)
                    author.suffix = suffix
                    author.save()

                    article.authors.add(author)

                print("* Imported {}".format(
                    article.get_full_identifier()
                ))

        except Exception as e:
            print("Cannot import {}: {}".format(
                issue.get_full_identifier(),
                e
            ))
