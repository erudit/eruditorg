# -*- coding: utf-8 -*-

from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from .models import Discipline
from .models import Journal
from .models import JournalInformation
from .models import IssueContributor


class JournalTranslationOptions(TranslationOptions):
    fields = (
        'name', 'subtitle',
    )


class JournalInformationTranslationOptions(TranslationOptions):
    fields = (
        'about', 'editorial_policy', 'subscriptions', 'team',
        'contact', 'partners',
    )


class DisciplineTranslationOptions(TranslationOptions):
    fields = (
        'name',
    )


class IssueContributorTranslationOptions(TranslationOptions):
    fields = (
        'role_name',
    )

translator.register(Journal, JournalTranslationOptions)
translator.register(JournalInformation, JournalInformationTranslationOptions)
translator.register(Discipline, DisciplineTranslationOptions)
translator.register(IssueContributor, IssueContributorTranslationOptions)
