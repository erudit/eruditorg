from django.shortcuts import render  # noq
from django.core.files.base import ContentFile
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from post_office import mail

from subscription.models import RenewalNotice
from subscription import report


def email(request):
    c = {}
    return render(request, 'subscription_renewal_email.html', context=c)


def confirm_test(request):
    ids = request.GET.get('ids').split(',')

    if request.POST.get('doit'):
        for renewal in RenewalNotice.objects.filter(pk__in=ids):
            report_data = report.generate_report(renewal)
            pdf = ContentFile(report_data)

            template = get_template('subscription_renewal_email.html')
            context = {'renewal_number': renewal.renewal_number}
            html_message = template.render(context)

            emails = mail.send(
                request.user.email,
                'erudit-abonnements@umontreal.ca',
                attachments={
                    '{}.pdf'.format(renewal.renewal_number): pdf
                },
                message=html_message,
                html_message=html_message,
                subject='{} - Avis de renouvellement'.format(
                    renewal.renewal_number
                )
            )

            renewal.sent_emails.add(
                emails
            )

            urls = reverse('admin:subscription_renewalnotice_changelist')
            return HttpResponseRedirect(urls)

            renewal.save()

    renewals = [
        r for r
        in RenewalNotice.objects.filter(pk__in=ids)
    ]

    return render(
        request,
        'send_email.html',
        context={
            'renewals': renewals,
            'test': 'TEST'
        }
    )

def confirm_send(request):
    c = {}
    return render(request, 'subscription_renewal_email.html', context=c)
