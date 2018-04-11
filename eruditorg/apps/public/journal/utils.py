from erudit.models import Issue, Article


def prepublication_querystring(object):

    if isinstance(object, Issue):
        issue = object
    elif isinstance(object, Article):
        issue = object.issue
    else:
        raise ValueError()
    return "ticket={ticket}".format(
        ticket=issue.prepublication_ticket
    )
