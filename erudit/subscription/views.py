from django.shortcuts import render  # noqa


def email(request):
    c = {}
    return render(request, 'subscription_renewal_email.html', context=c)
