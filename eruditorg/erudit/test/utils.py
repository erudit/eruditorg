from eruditarticle.objects.article import EruditArticle
from eruditarticle.objects.publication import EruditPublication
from eruditarticle.objects.journal import EruditJournal


def get_erudit_article(fixturename):
    with open('./tests/fixtures/article/{}'.format(fixturename), 'rb') as xml:
        return EruditArticle(xml.read())


def get_erudit_publication(fixturename):
    with open('./tests/fixtures/issue/{}'.format(fixturename), 'rb') as xml:
        return EruditPublication(xml.read())


def get_erudit_journal(fixturename):
    with open('./tests/fixtures/journal/{}'.format(fixturename), 'rb') as xml:
        return EruditJournal(xml.read())
