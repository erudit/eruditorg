# -*- coding: utf-8 -*-

from eulfedora import models
from eulfedora.rdfns import oai as oains
from eulxml.xmlmap import XmlObject


MODEL_PID_PREFIX = 'info:fedora/erudit-model:'


class JournalDigitalObject(models.DigitalObject):
    CONTENT_MODELS = [MODEL_PID_PREFIX + 'seriesCModel', ]
    publications = models.XmlDatastream('PUBLICATIONS', 'Publications', XmlObject)
    name = models.Relation(oains.setName)


class PublicationDigitalObject(models.DigitalObject):
    CONTENT_MODELS = [MODEL_PID_PREFIX + 'publicationCModel', ]
    publication = models.XmlDatastream('PUBLICATION', 'Publication', XmlObject)
    summary = models.XmlDatastream('SUMMARY', 'Summary', XmlObject)
    coverpage = models.FileDatastream(
        'COVERPAGE', 'Coverpage', defaults={'mimetype': 'image/jpeg', })
    pages = models.XmlDatastream('PAGES', 'Pages', XmlObject)


class ArticleDigitalObject(models.DigitalObject):
    CONTENT_MODELS = [MODEL_PID_PREFIX + 'unitCModel', ]
    erudit_xsd300 = models.XmlDatastream('ERUDITXSD300', 'Erudit XSD300', XmlObject)
    unit = models.XmlDatastream('UNIT', 'Unit', XmlObject)
    pdf = models.FileDatastream('PDF', 'PDF', defaults={'mimetype': 'application/pdf', })
