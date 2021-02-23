from .models import SiteMessage


def active_site_messages(request):
    """
    Get the public site messages for every template's context.
    """
    return {"site_messages": SiteMessage.objects.public()}
