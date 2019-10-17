from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from .models import Campaign


class CampaignTranslationOptions(TranslationOptions):
    fields = ("url", "image", "title", "alt")
    required_languages = ("fr", "en")


translator.register(Campaign, CampaignTranslationOptions)
