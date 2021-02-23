import logging
from .utils import remove_query_param, replace_query_param

logger = logging.getLogger(__name__)


class PaginationOutOfBoundsException(Exception):
    pass


class ResultsStats:
    def __init__(self, count, page, page_size):
        self.count = count
        self.page = page
        self.page_size = page_size

    @property
    def page_count(self):
        page_count = self.count // self.page_size
        if self.count > page_count * self.page_size:
            page_count += 1
        return page_count

    def next_page(self):
        if self.page >= self.page_count:
            return None
        else:
            return self.page + 1

    def prev_page(self):
        if self.page == 1:
            return None
        else:
            return self.page - 1

    def is_within_bounds(self):
        if self.page == 1:
            # page 1 is *always* within bounds, even when page_count == 0
            return True
        return 1 <= self.page <= self.page_count


def get_pagination_info(stats, request):

    if not stats.is_within_bounds():
        raise PaginationOutOfBoundsException()

    baseurl = request.build_absolute_uri()

    nextpage = stats.next_page()
    if nextpage:
        nexturl = replace_query_param(baseurl, "page", nextpage)
        lasturl = replace_query_param(baseurl, "page", stats.page_count)
    else:
        nexturl = None
        lasturl = None

    prevpage = stats.prev_page()
    if prevpage:
        firsturl = remove_query_param(baseurl, "page")
        if prevpage == 1:
            prevurl = firsturl
        else:
            prevurl = replace_query_param(baseurl, "page", prevpage)
    else:
        prevurl = None
        firsturl = None

    return {
        "count": stats.count,
        "num_pages": stats.page_count,
        "current_page": stats.page,
        "next_page": nextpage,
        "previous_page": stats.prev_page(),
        "page_size": stats.page_size,
        "links": {
            "next": nexturl,
            "last": lasturl,
            "previous": prevurl,
            "first": firsturl,
        },
    }
