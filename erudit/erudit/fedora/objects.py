# -*- coding: utf-8 -*-

from collections import OrderedDict

import lxml.etree as et

from eulfedora import models
from eulfedora.rdfns import oai as oains
from eulxml.xmlmap import XmlObject


MODEL_PID_PREFIX = 'info:fedora/erudit-model:'


class JournalDigitalObject(models.DigitalObject):
    """ Fedora objectf of a Journal """
    CONTENT_MODELS = [MODEL_PID_PREFIX + 'seriesCModel', ]
    publications = models.XmlDatastream('PUBLICATIONS', 'Publications', XmlObject)
    name = models.Relation(oains.setName)
    logo = models.FileDatastream('LOGO', 'Logo', defaults={'mimetype': 'image/jpeg', })
    oaiset_info = models.XmlDatastream('OAISET_INFO', 'OAISET Info', XmlObject)
    publications = models.XmlDatastream('PUBLICATIONS', 'Publications', XmlObject)

    @property
    def xml_content(self):
        """ Returns the XML content of the publications.

        The XML content comes from the ``PUBLICATIONS`` datastream.
        """
        return self.publications.content.serialize()


class PublicationDigitalObject(models.DigitalObject):
    """ Fedora object of an :py:class:`Issue <erudit.models.core.Issue>` """

    CONTENT_MODELS = [MODEL_PID_PREFIX + 'publicationCModel', ]
    publication = models.XmlDatastream('PUBLICATION', 'Publication', XmlObject)
    summary = models.XmlDatastream('SUMMARY', 'Summary', XmlObject)
    coverpage = models.FileDatastream(
        'COVERPAGE', 'Coverpage', defaults={'mimetype': 'image/jpeg', })
    pages = models.XmlDatastream('PAGES', 'Pages', XmlObject)

    @property
    def xml_content(self):
        """ Returns the XML content of the publication.

        The XML content comes from the ``SUMMARY`` datastream.
        """
        return self.summary.content.serialize()


class ArticleDigitalObject(models.DigitalObject):
    """ Fedora object of an article """

    CONTENT_MODELS = [MODEL_PID_PREFIX + 'unitCModel', ]
    erudit_xsd201 = models.XmlDatastream('ERUDITXSD201', 'Erudit XSD201', XmlObject)
    erudit_xsd300 = models.XmlDatastream('ERUDITXSD300', 'Erudit XSD300', XmlObject)
    infoimg = models.XmlDatastream('INFOIMG', 'INFOIMG', XmlObject)
    unit = models.XmlDatastream('UNIT', 'Unit', XmlObject)
    pdf = models.FileDatastream('PDF', 'PDF', defaults={'mimetype': 'application/pdf', })

    @property
    def xml_content(self):
        """ Return the XML content of the article

        An Article object contains datastreams for one or more of the
        following schema specifications.

        * ``ERUDITXSD300``: `ÉruditArticle 3.0`_
        * ``ERUDITXSD200``: `ÉruditArticle 2.0`_
        * ``SESAMEXSD``: ...

        In the case where an article contains multiple XML representation of itself,
        they will be processed in the following order:

        1. ``ERUDITXSD300``
        2. ``SESAMEXSD``
        3. ``ERUDITXSD200``

        Uses `liberuditarticle`_ to parse the content of the XML document and return
        a python object.

        :return: a python object representing the article's content

        .. _ÉruditArticle 3.0: http://www.erudit.org/xsd/article/3.0.0/doc/
        .. _ÉruditArticle 2.0: http://www.erudit.org/xsd/article/2.0.0/doc/
        .. _liberuditarticle: http://www.github.com/erudit/liberuditarticle/
        """
        if 'ERUDITXSD300' in self.ds_list:
            return self.erudit_xsd300.content.serialize()
        elif 'ERUDITXSD201' in self.ds_list:
            return self.erudit_xsd201.content.serialize()

    @property
    def infoimg_dict(self):
        """ Returns the content of the INFOIMG datastream as a dictionary. """
        infoimg_tree = et.fromstring(self.infoimg.content.serialize())
        infoimg_dict = OrderedDict()
        for im_tree in infoimg_tree.findall('im'):
            infoimg_dict.update({
                im_tree.get('id'): {
                    'src': im_tree.find('src//nomImg').text,
                    'plgr': im_tree.find('imPlGr//nomImg').text,
                },
            })
        return infoimg_dict


class MediaDigitalObject(models.DigitalObject):
    """ Fedora object of a media file. """

    CONTENT_MODELS = [MODEL_PID_PREFIX + 'mediaCModel', ]
    content = models.FileDatastream('CONTENT', 'CONTENT')
