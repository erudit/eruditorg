from collections import OrderedDict
from itertools import groupby

from django.core.management.base import BaseCommand
from django.db.models import Q

from erudit.models import Author, Journal
from ... import solr


def old_get_authors_dicts(journal):
    base_query = Q(
        lastname__isnull=False,
        article__issue__journal__id=journal.id,
        article__issue__is_published=True)
    qs = Author.objects.filter(base_query).order_by('lastname').distinct()
    qs = qs.exclude(firstname='', lastname='')
    grouped = groupby(
        sorted(qs, key=lambda a: a.letter_prefix), key=lambda a: a.letter_prefix)
    return OrderedDict([
        (g[0], sorted(list(g[1]), key=lambda a: a.lastname or a.othername)) for g in grouped])


class Command(BaseCommand):
    help = """Temporary command to compare old and new author article indexes.

    Because we're going to remove the `Author` model altogether soon, this command is going to be
    short-lived.
    """

    def handle(self, *args, **options):
        journals = Journal.objects.all()
        for journal in journals:
            if not journal.localidentifier:
                # fedora only
                continue
            if not journal.type:
                # some journals are bugged
                continue
            print("Benchtesting journal {}".format(journal.solr_code))
            self.benchtest_journal(journal)

    def benchtest_journal(self, journal):
        refdict = old_get_authors_dicts(journal)
        for letter, authors in refdict.items():
            for author in authors:
                if letter != author.lastname.strip()[:1].upper():
                    print("Interesting... {} in {}".format(author.lastname, letter))
        letters = solr.get_journal_authors_letters(journal.solr_code)
        if set(refdict) != letters:
            print("Not the same letters! added: {}, removed {}".format(
                letters - set(refdict), set(refdict) - letters))

        for letter in letters & set(refdict):
            authors_dict = solr.get_journal_authors_dict(journal.solr_code, letter, None)
            if len(authors_dict) != len(refdict[letter]):
                print("Not the same author count on letter {}! old: {} new {}".format(
                    letter, len(authors_dict), len(refdict[letter])))
