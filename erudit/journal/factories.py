# -*- coding: utf-8 -*-

import factory

from erudit.factories import JournalFactory


class JournalInformationFactory(factory.django.DjangoModelFactory):
    journal = factory.SubFactory(JournalFactory)

    class Meta:
        model = 'journal.journalinformation'
