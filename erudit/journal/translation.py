# -*- coding: utf-8 -*-

from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from .models import JournalInformation


class JournalInformationTranslationOptions(TranslationOptions):
    fields = (
        'about', 'editorial_policy', 'subscriptions', 'team',
        'contact', 'partners',
    )


translator.register(JournalInformation, JournalInformationTranslationOptions)
