# -*- coding:utf-8 -*-

from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class EruditDocumentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'num_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next_page': self.page.next_page_number() if self.page.has_next() else None,
                'previous_page': (
                    self.page.previous_page_number()if self.page.has_previous() else None),
                'page_size': self.page.paginator.per_page,
                'links': {
                   'next': self.get_next_link(),
                   'previous': self.get_previous_link(),
                },
            },
            'results': data,
        })

    def paginate(self, localidentifiers, queryset, request, view=None):
        """
        This is the default implementation of the PageNumberPagination.paginate_queryset method ;
        the only exception: the pagination is performed on a list of ordered localidentifiers.
        But the EruditDocument instances corresponding to the localidentifiers associated with the
        current page are returned.
        """
        page_size = self.get_page_size(request)
        if not page_size:  # pragma: no cover
            return None

        paginator = self.django_paginator_class(localidentifiers, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:  # pragma: no cover
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage:  # pragma: no cover
            msg = self.invalid_page_message.format(page_number=page_number)
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:  # pragma: no cover
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request

        current_localidentifiers = list(self.page)
        queryset = queryset.filter(localidentifier__in=current_localidentifiers)
        obj_dict = {obj.localidentifier: obj for obj in queryset}
        obj_list = [obj_dict[lid] for lid in current_localidentifiers]
        return obj_list
