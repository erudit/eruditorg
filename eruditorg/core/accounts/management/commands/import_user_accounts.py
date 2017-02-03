# -*- coding: utf-8 -*-

import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from erudit.models import Journal

from core.accounts.utils.mandragore import create_or_update_mandragore_user
from core.accounts.utils.mandragore import fetch_accounts_from_mandragore
from core.accounts.utils.mandragore import fetch_series_from_edinum
from core.accounts.utils.mandragore import MandragoreError
from core.accounts.utils.mandragore import user_coherent_with_mandragore
from core.accounts.utils.mandragore import get_journal_shortname_from_seriesid

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = """Import publisher accounts from a csv file"""

    def handle(self, *args, **options):

        self.created_or_updated_publishers = []
        self.created_or_updated_journals = []

        persons_to_add = {}

        # The data required to create the user accounts is in Edinum
        # and Mandragore.
        #
        # We need to manually join between the databases, so we keep
        # local association tables for this.
        person_ids_to_fetch = set()
        persons_collections = {}
        collections_journals = {}

        # Retrieve the accounts from Mandragore
        for (username, email, person_id,
             collectionid) in fetch_accounts_from_mandragore():
            user = User.objects.filter(username=username)
            if user.exists():
                user = user.first()
                user_coherent, message = user_coherent_with_mandragore(
                    user, {
                        'username': username,
                        'person_id': person_id
                    }
                )
                if not user_coherent:
                    raise MandragoreError(
                        "Error importing user {}: {}".format(username, message)  # noqa
                    )

            person_ids_to_fetch.add(person_id)
            persons_collections[person_id] = collectionid

            user = create_or_update_mandragore_user(
                person_id, email=email, username=username
            )

            persons_to_add[person_id] = user

        # Update the accounts with the values from Edinum
        #     middlename, familyname) in fetch_users_from_edinum(
        #         person_ids_to_fetch):
        #    user = persons_to_add[person_id]

        # Add the users to the journal
        for (id, journal_id) in fetch_series_from_edinum(persons_collections.values()):
            collections_journals[id] = journal_id
        for person_id, collection in persons_collections.items():
            try:
                journal_id = collections_journals[collection]
                shortname = get_journal_shortname_from_seriesid(journal_id)
                journal = Journal.objects.get(code=shortname[0])
                to_add = persons_to_add[person_id]
                to_add.save()

                journal.members.add(to_add)
                journal.save()
            except KeyError as e:
                print("keyerror")
                print(e)
            except Journal.DoesNotExist as e:
                print(shortname, " does not exist.")
            except Exception as e:
                log.error(
                    e
                )
                raise
