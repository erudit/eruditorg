# -*- coding: utf-8 -*-

import os.path as op

from django.conf import settings
from django.core.management.base import BaseCommand
import lxml.etree as et

from ...models import Discipline
from ...models import Journal

FIXTURE_ROOT = getattr(
    settings, 'JOURNAL_FIXTURES',
    op.join(op.dirname(__file__), 'fixtures')
)

SUPPORTED_LANGUAGES = [lang[0] for lang in settings.LANGUAGES]


class Command(BaseCommand):
    help = """Import disciplines from XML files"""

    def handle(self, *args, **options):
        disciplines_xmls = []
        with open(FIXTURE_ROOT + '/disciplines.xml', 'rb') as fp:
            disciplines_xmls.append(fp.read())
        with open(FIXTURE_ROOT + '/disciplines_culturelle.xml', 'rb') as fp:
            disciplines_xmls.append(fp.read())

        discipline_id_correspondences = {}

        # Creates all the discipline instances
        for xml in disciplines_xmls:
            dom = et.fromstring(xml)

            for discipline_xml in dom.findall('.//discipline'):
                dcode = discipline_xml.find('.//clef_i18n').text
                try:
                    discipline = Discipline.objects.get(code=dcode)
                except Discipline.DoesNotExist:
                    discipline = Discipline()
                    discipline.code = dcode
                for intitule_xml in discipline_xml.findall('.//intitule'):
                    lang = intitule_xml.get('lang')
                    if lang not in SUPPORTED_LANGUAGES:
                        continue
                    setattr(discipline, 'name_' + intitule_xml.get('lang'), intitule_xml.text)

                discipline.save()
                discipline_id_correspondences[discipline_xml.get('id')] = discipline
                print('Imported: "{}" discipline'.format(discipline.name))

        discipline_journals_xmls = []
        with open(FIXTURE_ROOT + '/revues.xml', 'rb') as fp:
            discipline_journals_xmls.append(fp.read())
        with open(FIXTURE_ROOT + '/revues_culturelle.xml', 'rb') as fp:
            discipline_journals_xmls.append(fp.read())

        # Associates the Discipline instances with Journal instances
        for xml in discipline_journals_xmls:
            dom = et.fromstring(xml)

            for journal_xml in dom.findall('.//revue'):
                try:
                    journal = Journal.legacy_objects.get_by_id(code=journal_xml.get('code'))
                except Journal.DoesNotExist:
                    print('Unable to find the following Journal instance: {}'.format(
                        journal_xml.get('code')))
                    continue

                for discipline_xml in journal_xml.findall('.//discipline'):
                    discipline = discipline_id_correspondences.get(discipline_xml.text)
                    journal.disciplines.add(discipline)

                print('Imported: {}\'s disciplines'.format(journal.code))
