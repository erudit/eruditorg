import urllib.parse as urlparse
from django import template

register = template.Library()


@register.inclusion_tag("public/search/_pagination.html", takes_context=True)
def search_result_pagination(context, ):
    request = context["request"]
    current_page = context.get("current_page", 1)
    page_count = context.get("page_count", 1)

    # Split current URL in base path and params
    url_parse_result = urlparse.urlsplit(request.get_full_path())
    base_path = url_parse_result.path
    params = dict(urlparse.parse_qsl(url_parse_result.query))

    pages_urls = []
    for page_number in range(page_count):
        params["page"] = (page_number + 1)

        params_string = "&".join(
            "{key}={val}".format(key=key, val=val) for (key, val) in params.items()
        )
        page_url = "{base_path}?{params_string}".format(
            base_path=base_path,
            params_string=params_string
        )

        pages_urls.append({"page": (page_number + 1), "url": page_url})

    return {"pages_urls": pages_urls, "current_page": current_page, "page_count": page_count}
