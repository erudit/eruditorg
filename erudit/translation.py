# -*- coding: utf-8 -*-

from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from .models import Discipline
from .models import Journal
from .models import Issue
from .models import JournalInformation


class JournalTranslationOptions(TranslationOptions):
    fields = (
        'name', 'subtitle',
    )


class IssueTranslationOptions(TranslationOptions):
    fields = (
        'formatted_volume_title',
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


translator.register(Journal, JournalTranslationOptions)
translator.register(JournalInformation, JournalInformationTranslationOptions)
translator.register(Issue, IssueTranslationOptions)
translator.register(Discipline, DisciplineTranslationOptions)
