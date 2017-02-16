# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connections
from django.db import transaction
from django.db.utils import OperationalError
from django.db.models import Q
from erudit.models import Journal

from core.accounts.models import LegacyAccountProfile
from core.accounts.shortcuts import get_or_create_legacy_user

from .drupalerudit_models import Users
from .drupalerudit_models import UsersRoles


class ImportException(Exception):
    pass


class Command(BaseCommand):
    args = '<action:import_users>'
    help = 'Import data from the "drupalerudit" database'

    def handle(self, *args, **options):
        if len(args) == 0:
            self.stdout.write(self.args)
            return

        self.args = args
        command = args[0]
        self.stdout.write(command)
        cmd = getattr(self, command)
        cmd()

    def import_users(self):
        drupal_users = Users.objects.filter(~Q(name='admin'), ~Q(name=''))

        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "drupalerudit" users ({0} users to import!)'.format(
                drupal_users.count()
            )))

        # Patches the existing database so that we can retrieve some values from journal-specific
        # databases.
        journal_codes = Journal.objects.filter(collection__code='erudit') \
            .values_list('code', flat=True)
        base_conf = connections.databases['drupalerudit']
        for jcode in journal_codes:
            connections.databases['drupalerudit_' + jcode] = {
                'ENGINE': base_conf.get('ENGINE'),
                'NAME': 'drupalerudit_' + jcode,
                'USER': base_conf.get('USER'),
                'PASSWORD': base_conf.get('PASSWORD'),
                'HOST': '',
            }

        for drupal_user in drupal_users:
            try:
                self._import_drupal_user(drupal_user)
            except ImportException:
                pass

    @transaction.atomic
    def _import_drupal_user(self, drupal_user):
        self.stdout.write(self.style.MIGRATE_LABEL(
            '    Start importing the Drupal user with ID: {0}'.format(drupal_user.uid)),
            ending='')

        # STEP 1: creates a user instance
        # --

        try:
            legacy_profile = LegacyAccountProfile.objects \
                .filter(origin=LegacyAccountProfile.DB_DRUPAL).get(legacy_id=str(drupal_user.uid))
            user = legacy_profile.user
        except LegacyAccountProfile.DoesNotExist:
            user, _ = get_or_create_legacy_user(
                username=drupal_user.name, email=drupal_user.mail,
                hashed_password='drupal$' + drupal_user.pass_field)
            LegacyAccountProfile.objects.create(
                user=user, legacy_id=str(drupal_user.uid), origin=LegacyAccountProfile.DB_DRUPAL)

        # STEP 2: associates the user to the proper Journal instances
        # --

        # roles = Role.objects.all()
        # roles_dict = {r.rid: r for r in roles}  # noqa ; should we use this?
        journals = Journal.objects.filter(collection__code='erudit')
        for journal in journals:
            db_id = 'drupalerudit_' + journal.code
            try:
                drupal_user_roles = list(
                    UsersRoles.objects.using(db_id).filter(uid=drupal_user.uid)
                    .values_list('rid'))
            except OperationalError:
                self.stdout.write(self.style.WARNING('  inexistant DB: "{}"'.format(db_id)))

            if drupal_user_roles:
                # Add the user to the members of the considered Journal
                journal.members.add(user)

        self.stdout.write(self.style.SUCCESS('  [OK]'))
