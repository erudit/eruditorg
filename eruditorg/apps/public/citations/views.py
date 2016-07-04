# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.views.generic import View

from base.http import JsonAckResponse
from base.http import JsonErrorResponse
from core.metrics.viewmixins import MetricCaptureMixin
from erudit.models import EruditDocument


class SavedCitationAddView(MetricCaptureMixin, View):
    """ Add an Érudit document to the list of documents associated to the current user. """
    http_method_names = ['post', ]
    tracking_metric_name = 'erudit__citation__add'

    def post(self, request, document_id):
        document = get_object_or_404(EruditDocument, pk=document_id)
        self.request.saved_citations.add(document)
        return JsonAckResponse(saved_document_id=document.id)


class SavedCitationRemoveView(MetricCaptureMixin, View):
    """ Remove an Érudit document from the list of documents associated to the current user. """
    http_method_names = ['post', ]
    tracking_metric_name = 'erudit__citation__remove'

    def post(self, request, document_id):
        document = get_object_or_404(EruditDocument, pk=document_id)
        try:
            self.request.saved_citations.remove(document)
        except KeyError:
            return JsonErrorResponse(ugettext("Ce document n'est pas présent dans les notices"))
        return JsonAckResponse(removed_document_id=document.id)
