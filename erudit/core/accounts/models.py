# -*- coding: utf-8 -*-

import hashlib
from random import choice
import base64

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.email import Email


class AbonnementProfile(models.Model):
    """
    Personal account used in erudit.org to access protected content.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'))
    password = models.CharField(max_length=50, verbose_name=_("Mot de passe"), blank=True)

    class Meta:
        verbose_name = _("Compte personnel")
        verbose_name_plural = _("Comptes personnels")

    def save(self, *args, **kwargs):
        # Password encryption
        if self.pk:
            if AbonnementProfile.objects.filter(pk=self.pk).count() == 1:
                old_crypted_password = AbonnementProfile.objects.get(pk=self.pk).password
                if not (self.password == old_crypted_password):
                    self.update_password(self.password)
            else:
                # Not yet in Db, so the password is set in constructor already crypted
                pass
        else:
            self.mail_account()
            new_password = self.generate_password()
            self.update_password(new_password)
        super(AbonnementProfile, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {} ({})'.format(self.user.first_name, self.user.last_name, self.id)

    def generate_password(self):
        return ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789%*(-_=+)') for i in range(8)])

    def update_password(self, plain_password):
        self.password = self.sha1(plain_password)

    def mail_account(self):
        email = Email(
            [self.user.email, ],
            html_template='userspace/journal/subscription/mail/new_account.html',
            subject=_('erudit.org : création de votre compte'),
            extra_context={'object': self})
        email.send()

    def sha1(self, msg, salt=None):
        "Crypt function from legacy system"
        if salt is None:
            salt = settings.INDIVIDUAL_SUBSCRIPTION_SALT
        to_sha = msg.encode('utf-8') + salt.encode('utf-8')
        hashy = hashlib.sha1(to_sha).digest()
        return base64.b64encode(hashy + salt.encode('utf-8')).decode('utf-8')


class MandragoreProfile(models.Model):
    """ Store variables that are related to this user's Mandragore profile. """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'))

    synced_with_mandragore = models.BooleanField(
        verbose_name=_("Synchronisé avec Mandragore"), default=False)
    """ Determines if this particular object is synced with the Edinum database """  # noqa

    mandragore_id = models.CharField(
        max_length=7, blank=True, null=True, verbose_name=_('Identifiant Mandragore'))
    """ The Mandragore person_id for this User """

    sync_date = models.DateField(blank=True, null=True)
    """ Date at which the model was last synchronized with Mandragore """
