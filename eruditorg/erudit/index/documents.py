# -*- coding: utf-8 -*-

from .conf import settings as index_settings


def get_bulk_operation_metadata(erudit_document):
    """ Returns the bulk operation metadata associated wit the considered Érudit document. """
    return {
        'index': {
            '_index': index_settings.ES_INDEX_NAME,
            '_type': index_settings.ES_INDEX_DOC_TYPE,
            '_id': erudit_document.localidentifier,
        }
    }


def get_article_document_from_fedora(article):
    """ Returns a dictionary corresponding to the given article by using Fedora. """
    issue = article.issue
    return {
        'localidentifier': article.localidentifier,
        'publication_year': issue.erudit_object.publication_year,
        'number': issue.erudit_object.number,
        'authors': [
            '{0} {1}'.format(a['firstname'], a['lastname']) for a in article.erudit_object.authors],
        'issn': article.erudit_object.issn,
        # 'isbn': ???,
    }
