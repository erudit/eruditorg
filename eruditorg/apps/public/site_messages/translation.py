from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from .models import SiteMessage


class SiteMessageTranslationOptions(TranslationOptions):
    fields = (
        'message',
    )
    required_languages = (
        'fr',
        'en',
    )


translator.register(SiteMessage, SiteMessageTranslationOptions)
