from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from .models import Discipline
from .models import JournalInformation
from .models import JournalType


class JournalInformationTranslationOptions(TranslationOptions):
    fields = (
        'about', 'editorial_policy', 'subscriptions', 'team',
        'contact', 'partners',
    )


class DisciplineTranslationOptions(TranslationOptions):
    fields = (
        'name',
    )


class JournalTypeTranslationOptions(TranslationOptions):
    fields = (
        'name',
    )


translator.register(JournalInformation, JournalInformationTranslationOptions)
translator.register(JournalType, JournalTypeTranslationOptions)
translator.register(Discipline, DisciplineTranslationOptions)
