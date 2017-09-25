# -*- coding: utf-8 -*-

import csv
import os

from django.core.management.base import BaseCommand
from django.db import connections

from core.accounts.models import LegacyAccountProfile
from erudit.models import Journal
from erudit.models import Organisation

from ..models import JournalAccessSubscription

from .legacy_models import Abonneindividus


class Command(BaseCommand):
    args = '<action:total_abonnes|list_abonnes|import_abonnes>'
    help = 'Import data from legacy system'

    def handle(self, *args, **options):
        """
        Command dispatcher
        """
        if len(args) == 0:
            self.stdout.write(self.args)
            return

        self.args = args
        command = args[0]
        self.stdout.write(command)
        cmd = getattr(self, command)
        cmd()

    def list_abonnes(self):
        for abonne in Abonneindividus.objects.all():
            self.stdout.write(abonne.courriel)

    def total_abonnes(self):
        self.stdout.write(str(Abonneindividus.objects.count()))

    def link_abonnes_from_csv(self):
        # Create policy from filename if it does not exist
        filename = self.args[1]
        basename = os.path.basename(filename)
        if '.' in basename:
            basename = basename.split('.')[0]
        try:
            organization = Organisation.objects.get(name__iexact=basename)  # noqa
        except Organisation.DoesNotExist:
            organization = Organisation.objects.create(name=basename)

        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                email = row[2]
                journal_id = row[3]

                # Assign the policy to the account
                try:
                    profile = LegacyAccountProfile.objects.\
                        get(origin=LegacyAccountProfile.DB_ABONNEMENTS, user__email__iexact=email)
                except Exception:
                    print('{} {}'.format('account', email))
                    continue

                # Define the journal in the policy

                if Journal.objects.filter(id=journal_id).count() == 1:
                    journal = Journal.objects.get(id=journal_id)
                    JournalAccessSubscription.objects.create(
                        journal=journal, user=profile.user, sponsor=organization)

    def link_abonnes_from_acces(self):
        abonne_profiles = LegacyAccountProfile.objects \
            .filter(origin=LegacyAccountProfile.DB_ABONNEMENTS)
        cursor = connections['legacy_subscription'].cursor()

        journals_account_volumetry = {"": []}

        for profile in abonne_profiles:
            sql = "SELECT revueID FROM revueindividus \
WHERE abonneIndividusID = {}".format(profile.legacy_id)
            cursor.execute(sql)
            journals = []
            rows = cursor.fetchall()

            if len(rows) == 0:
                journals_account_volumetry[""].append(profile)

            for row in rows:
                try:
                    journal = Journal.objects.get(id=row[0])
                    journals.append(journal)
                except Journal.DoesNotExist:
                    pass

                jids = sorted([j.id for j in journals])
                key = "|".join([str(j) for j in jids])
                if key not in journals_account_volumetry:
                    journals_account_volumetry[key] = []
                journals_account_volumetry[key].append(profile)

        for k, profiles in journals_account_volumetry.items():
            # Not any access
            if k is '':
                for p in profiles:
                    p.user.is_active = False
                    p.user.save()

            # Journal subscription
            if k is not '' and len(k.split('|')) == 1 and len(profiles) > 1:
                journal = Journal.objects.get(id=k)
                for p in profiles:
                    JournalAccessSubscription.objects.create(
                        journal=journal, user=p.user)

            # Individual policy
            if k is not '' and len(profiles) == 1:
                profile = profiles[0]
                ids = k.split('|')
                journals = Journal.objects.filter(id__in=ids)
                for journal in journals:
                    JournalAccessSubscription.objects.create(
                        journal=journal, user=profile.user)
