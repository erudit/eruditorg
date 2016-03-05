import hashlib
import ipaddress
from random import choice
import base64
from datetime import timedelta
from functools import reduce

from django.conf import settings
from django.utils import timezone
from django.db import models
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from post_office import mail

from erudit.models import Organisation as CoreOrganisation
from erudit.models import Journal as CoreJournal


# When a notification is sent, don't spam users until this elapsed time
EVENT_SILENCE_DAYS = getattr(settings, "EVENT_SILENCE_DAYS ", 30)


class Organisation(CoreOrganisation):
    class Meta:
        proxy = True


class Journal(CoreJournal):
    class Meta:
        proxy = True
        verbose_name = _('Revue')


class IndividualAccountProfile(models.Model):
    """
    Personal account used in erudit.org
    to access protected content.
    An account should always be linked with a policy, which determines its
    access rights.
    The policy itself is linked either with an account or an organization.
    """
    user = models.OneToOneField(User, verbose_name=_('Utilisateur'))
    password = models.CharField(max_length=50, verbose_name=_("Mot de passe"), blank=True)
    policy = models.ForeignKey(
        "Policy",
        verbose_name=_("Accès"),
        related_name="accounts",
        blank=True,
        null=True,
        help_text=_("Laisser vide si la politique d'accès aux produits est définie plus bas")
    )

    class Meta:
        verbose_name = _("Compte personnel")
        verbose_name_plural = _("Comptes personnels")

    def save(self, *args, **kwargs):
        # Stamp first user created date
        # TODO userspace allow empty selection for policy
        if not self.pk and self.policy.date_activation is None:
            self.policy.date_activation = timezone.now()
            self.policy.date_renew = self.policy.date_activation
            self.policy.renew()

        # Password encryption
        if self.pk:
            if IndividualAccountProfile.objects.filter(pk=self.pk).count() == 1:
                old_crypted_password = IndividualAccountProfile.objects.get(pk=self.pk).password
                if not (self.password == old_crypted_password):
                    self.update_password(self.password)
            else:
                # Not yet in Db, so the password is set in constructor already crypted
                pass
        else:
            self.mail_account()
            new_password = self.generate_password()
            self.update_password(new_password)
        super(IndividualAccountProfile, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {} ({})'.format(self.user.first_name, self.user.last_name, self.id)

    def generate_password(self):
        return ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789%*(-_=+)') for i in range(8)])

    def update_password(self, plain_password):
        self.password = self.sha1(plain_password)
        self.mail_password(plain_password)

    def mail_password(self, plain_password):
        template = get_template('userspace/subscription/mail/new_password.html')
        context = {'object': self, 'plain_password': plain_password, }
        html_message = template.render(context)
        recipient = self.user.email
        mail.send(
            recipient,
            settings.RENEWAL_FROM_EMAIL,
            message=html_message,
            html_message=html_message,
            subject=_("erudit.org : mot de passe")
        )

    def mail_account(self):
        template = get_template('userspace/subscription/mail/new_account.html')
        context = {'object': self}
        html_message = template.render(context)
        recipient = self.user.email
        mail.send(
            recipient,
            settings.RENEWAL_FROM_EMAIL,
            message=html_message,
            html_message=html_message,
            subject=_("erudit.org : création de votre compte")
        )

    def sha1(self, msg, salt=None):
        "Crypt function from legacy system"
        if salt is None:
            salt = settings.INDIVIDUAL_SUBSCRIPTION_SALT
        to_sha = msg.encode('utf-8') + salt.encode('utf-8')
        hashy = hashlib.sha1(to_sha).digest()
        return base64.b64encode(hashy + salt.encode('utf-8')).decode('utf-8')


class InstitutionalAccount(models.Model):
    """
    An institutional account defines how an institution can access
    protected content.
    """
    institution = models.ForeignKey(CoreOrganisation, verbose_name=_('Organisation'))
    policy = models.ForeignKey(
        'Policy', verbose_name=_('Accès'), related_name='institutional_accounts')
    badge = models.ImageField(
        verbose_name=_('Badge'), blank=True, null=True,
        upload_to='institutional_accounts_badges')

    class Meta:
        verbose_name = _('Compte institutionnel')
        verbose_name_plural = _('Comptes institutionnel')

    def __str__(self):
        return str(self.institution)


class InstitutionIPAddressRange(models.Model):
    institutional_account = models.ForeignKey(
        InstitutionalAccount, verbose_name=_('Compte institutionnel'))
    ip_start = models.GenericIPAddressField(verbose_name=_('Adresse IP de début'))
    ip_end = models.GenericIPAddressField(verbose_name=_('Adresse IP de fin'))

    class Meta:
        verbose_name = _('Plage d\'adresses IP d\'institution')
        verbose_name_plural = _('Plages d\'adresses IP d\'institution')

    def __str__(self):
        return '{institution} / {start} - {end}'.format(
            institution=self.institutional_account, start=self.ip_start, end=self.ip_end)

    def clean(self):
        super(InstitutionIPAddressRange, self).clean()
        start = ipaddress.ip_address(self.ip_start)
        end = ipaddress.ip_address(self.ip_end)
        if start > end:
            raise ValidationError(_(
                'L\'adresse IP de début doit être inférieure à l\'adresse IP de fin'))

    @property
    def ip_addresses(self):
        """ Returns the list of IP addresses contained in the current range. """
        start = ipaddress.ip_address(self.ip_start)
        end = ipaddress.ip_address(self.ip_end)
        return reduce(
            lambda ips, ipn: ips + list(ipn),
            ipaddress.summarize_address_range(start, end), [])


class PolicyEvent(models.Model):
    """
    """
    date_creation = models.DateTimeField(
        editable=False,
        null=True,
        default=timezone.now,
        verbose_name=_("Date de création")
    )
    policy = models.ForeignKey(
        'Policy',
        verbose_name=_('Accès aux produits'),
    )
    code = models.CharField(
        max_length=120,
        verbose_name=_("Code"),
        choices=(
                ('LIMIT_REACHED', _('Limite atteinte')),
        )
    )
    message = models.TextField(verbose_name=_("Texte"), blank=True)

    class Meta:
        verbose_name = _("Évènement sur les accès")
        verbose_name_plural = _("Évènements sur les accès")
        ordering = ('-date_creation', )


class Policy(models.Model):
    """
    Entity which describe who and what resource, an organization can access.
    (Wikipedia, AEIQ, Revue).
    date activation is stamp as soon as the first account is created
    """
    # this field store __str__ value with generic relation info which is
    # stressfully for the database
    generated_title = models.CharField(max_length=120, verbose_name=_("Titre"),
                                       blank=True,
                                       editable=False)
    date_creation = models.DateTimeField(
        editable=False,
        null=True,
        default=timezone.now,
        verbose_name=_("Date de création")
    )
    date_modification = models.DateTimeField(
        editable=False,
        null=True,
        default=timezone.now,
        verbose_name=_("Date de modification")
    )
    date_activation = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Date d'activation"),
        help_text=_("Ce champs se remplit automatiquement. \
            Il est éditable uniquement pour les données existantes qui n'ont pas cette information")
    )
    date_renew = models.DateTimeField(
        null=True,
        verbose_name=_("Date de renouvellement")
    )
    renew_cycle = models.PositiveSmallIntegerField(
        verbose_name=_("Cycle du renouvellement (en jours)"),
        default=365,
    )

    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=models.Q(
            app_label='erudit', model__in=('organisation', 'journal')
        ) | models.Q(model='individualaccount'),
        verbose_name=_('Type'),
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField()

    comment = models.TextField(verbose_name=_("Commentaire"), blank=True)

    max_accounts = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum de comptes"),
        blank=True,
        null=True,
    )

    access_full = models.BooleanField(
        default=False,
        verbose_name=_("Accès à tous les produits")
    )

    access_journal = models.ManyToManyField(
        "erudit.journal",
        verbose_name=_("Revues"),
        blank=True,
    )

    managers = models.ManyToManyField(
        "auth.User",
        verbose_name=_("Gestionnaires des comptes"),
        blank=True,
        related_name='organizations_managed',
    )

    class Meta:
        verbose_name = _("Accès aux produits")
        verbose_name_plural = _("Accès aux produits")

    @property
    def total_accounts(self):
        return self.accounts.count()

    def __str__(self):
        if not self.generated_title and self.pk:
            self.generated_title = '{} [{}#{}]'.format(
                self.content_object, self.content_type, self.id)
            self.save()
        return self.generated_title

    def save(self, *args, **kwargs):
        self.date_modification = timezone.now()
        super(Policy, self).save(*args, **kwargs)

    def renew(self):
        if self.date_activation is None:
            raise ValidationError(_("Il n'y a pas de date d'activiation de spécifiée"))
        if self.date_renew is None:
            self.date_renew = self.date_activation
        self.date_renew = self.date_renew + timedelta(days=self.renew_cycle)
        self.save()

    def notify_limit_reached(self):
        if self.max_accounts and self.total_accounts > self.max_accounts:
            date = timezone.now() - timedelta(days=EVENT_SILENCE_DAYS)
            if PolicyEvent.objects.filter(policy=self, date_creation__gt=date).count() == 0:
                template = get_template('userspace/subscription/mail/limit_reached.html')
                context = {'policy': self}
                html_message = template.render(context)

                recipients = [u.email for u in self.managers.all() if u.email]
                mail.send(
                    recipients,
                    settings.RENEWAL_FROM_EMAIL,
                    message=html_message,
                    html_message=html_message,
                    subject=_("Avis de dépassement") + '#{}'.format(self.id)
                )

                if len(recipients) > 0:
                    emails = ",".join(recipients)
                else:
                    emails = "!!!"
                msg = "Destinataires: {} Message: {}".format(emails, html_message)
                PolicyEvent(policy=self, code='LIMIT_REACHED', message=msg).save()
