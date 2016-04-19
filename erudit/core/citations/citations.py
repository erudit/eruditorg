# -*- coding: utf-8 -*-

from erudit.models import Article

from .models import SavedCitationList as DBSavedCitationList


class SavedCitationList(set):
    """ Stores a set of article citations. """

    def __init__(self, request, name='saved-citations', *args, **kwargs):
        super(SavedCitationList, self).__init__(*args, **kwargs)
        self.request = request
        self.name = name
        self.update(request.session.get(self.name, []))

    def save(self):
        """ Saves a list of citations into the user's session. """
        self.request.session[self.name] = list(self)
        # If the user is authenticated the list of articles should be associated to the User
        # instance by creating or updating a SavedCitationList instance.
        if self.request.user.is_authenticated() and len(self):
            db_clist, _ = DBSavedCitationList.objects.get_or_create(user=self.request.user)
            db_clist.articles.add(*Article.objects.filter(id__in=list(self)))

    def add(self, article):
        article_id = article.id if isinstance(article, Article) else article
        super(SavedCitationList, self).add(article_id)

    def remove(self, article):
        article_id = article.id if isinstance(article, Article) else article
        super(SavedCitationList, self).remove(article_id)
