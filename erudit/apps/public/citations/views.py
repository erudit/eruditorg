# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.views.generic import View

from base.http import JsonAckResponse
from base.http import JsonErrorResponse
from erudit.models import Article


class SavedCitationAddView(View):
    """ Add an article to the list of saved articles associated to the current user. """
    http_method_names = ['post', ]

    def post(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id)
        self.request.saved_citations.add(article)
        return JsonAckResponse(saved_article_id=article.id)


class SavedCitationRemoveView(View):
    """ Remove an article from the list of saved articles associated to the current user. """
    http_method_names = ['post', ]

    def post(self, request, article_id):
        article = get_object_or_404(Article, pk=article_id)
        try:
            self.request.saved_citations.remove(article)
        except KeyError:
            return JsonErrorResponse(ugettext("Cet article n'est pas présent dans les notices"))
        return JsonAckResponse(removed_article_id=article.id)
