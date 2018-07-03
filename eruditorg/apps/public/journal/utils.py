from erudit.models import Issue, Article


def prepublication_querystring(object):

    if isinstance(object, Issue):
        issue = object
    elif isinstance(object, Article):
        issue = object.issue
    else:
        raise ValueError()
    if issue.is_published:
        return None
    return "ticket={ticket}".format(
        ticket=issue.prepublication_ticket
    )
