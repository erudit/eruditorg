from .utils import remove_query_param, replace_query_param


def get_pagination_info(stats, request):
    if not stats.count:
        return None

    baseurl = request.build_absolute_uri()

    nextpage = stats.next_page()
    if nextpage:
        nexturl = replace_query_param(baseurl, 'page', nextpage)
        lasturl = replace_query_param(baseurl, 'page', stats.page_count)
    else:
        nexturl = None
        lasturl = None

    prevpage = stats.prev_page()
    if prevpage:
        firsturl = remove_query_param(baseurl, 'page')
        if prevpage == 1:
            prevurl = firsturl
        else:
            prevurl = replace_query_param(baseurl, 'page', prevpage)
    else:
        prevurl = None
        firsturl = None

    return {
        'count': stats.count,
        'num_pages': stats.page_count,
        'current_page': stats.page,
        'next_page': nextpage,
        'previous_page': stats.prev_page(),
        'page_size': stats.page_size,
        'links': {
            'next': nexturl,
            'last': lasturl,
            'previous': prevurl,
            'first': firsturl,
        },
    }
