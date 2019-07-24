import re
from contextlib import contextmanager
from collections import defaultdict
from lxml import etree
from lxml.builder import E

from eulfedora.api import ApiFacade
from eulfedora.util import RequestFailed

from .domchange import (
    EruditArticleDomChanger, EruditPublicationDomChanger, EruditJournalDomChanger
)

# NOTE: This fake API is far from complete but is enough to make tests pass
#       as they are now. We'll have to improve this as we expand testing areas.

FAKE_FEDORA_PROFILE = """<?xml version="1.0" encoding="UTF-8"?>
<objectProfile
    xmlns="http://www.fedora.info/definitions/1/0/access/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.fedora.info/definitions/1/0/access/
    http://www.fedora.info/definitions/1/0/objectProfile.xsd"
    pid="{pid}" >
<objLabel>Publication Erudit</objLabel>
<objOwnerId></objOwnerId>
<objModels>
<model>info:fedora/erudit-model:publicationCModel</model>
<model>info:fedora/fedora-system:FedoraObject-3.0</model>
</objModels>
<objCreateDate>2010-08-03T18:22:20.635Z</objCreateDate>
<objLastModDate>2011-08-11T14:52:01.878Z</objLastModDate>
<objDissIndexViewURL>{full_url}/methods/fedora-system%3A3/viewMethodIndex</objDissIndexViewURL>
<objItemIndexViewURL>{full_url}/methods/fedora-system%3A3/viewItemIndex</objItemIndexViewURL>
<objState>A</objState>
</objectProfile>
"""

FAKE_JOURNAL_DATASTREAM_LIST = """<?xml version="1.0" encoding="UTF-8"?>
<objectDatastreams
    xmlns="http://www.fedora.info/definitions/1/0/access/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.fedora.info/definitions/1/0/access/
    http://www.fedora-commons.org/definitions/1/0/listDatastreams.xsd"
    pid="{pid}"
    baseURL="http://fakeurl/">
<datastream dsid="SERIES" label="SERIES" mimeType="text/xml" />
<datastream dsid="DC" label="Dublin Core Record for this object" mimeType="text/xml" />
<datastream dsid="LOGO" label="LOGO" mimeType="image/jpeg" />
<datastream dsid="PUBLICATIONS_HIDDEN" label="PUBLICATIONS_HIDDEN" mimeType="text/xml" />
<datastream dsid="RELS-EXT" label="Relationships" mimeType="application/rdf+xml" />
<datastream dsid="OAISET_INFO" label="Description de la revue en DC" mimeType="text/xml" />
<datastream dsid="PUBLICATIONS" label="PUBLICATIONS" mimeType="text/xml" />
<datastream dsid="THEMES" label="THEMES" mimeType="text/xml" />
</objectDatastreams>
"""

FAKE_ISSUE_DATASTREAM_LIST = """<?xml version="1.0" encoding="UTF-8"?>
<objectDatastreams
    xmlns="http://www.fedora.info/definitions/1/0/access/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.fedora.info/definitions/1/0/access/ http://www.fedora-commons.org/definitions/1/0/listDatastreams.xsd"
    pid="{pid}"
    baseURL="http://fakeurl/">
<datastream dsid="PAGES" label="PAGES" mimeType="text/xml" />
<datastream dsid="PUBLICATION" label="PUBLICATION" mimeType="text/xml" />
<datastream dsid="DC" label="Dublin Core Record for this object" mimeType="text/xml" />
<datastream dsid="RELS-EXT" label="Relationships" mimeType="application/rdf+xml" />
<datastream dsid="SUMMARY" label="SUMMARY" mimeType="text/xml" />
</objectDatastreams>
""" # noqa

FAKE_PAGE_DATASTREAM_LIST = """<?xml version="1.0" encoding="UTF-8"?>
<objectDatastreams
    xmlns="http://www.fedora.info/definitions/1/0/access/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.fedora.info/definitions/1/0/access/ http://www.fedora-commons.org/definitions/1/0/listDatastreams.xsd"
    pid="{pid}"
    baseURL="http://fakeurl/">
<datastream dsid="IMAGE" label="IMAGE" mimeType="image/jpeg" />
</objectDatastreams>
""" # noqa

FAKE_ARTICLE_DATASTREAM_LIST = """<?xml version="1.0" encoding="UTF-8"?>
<objectDatastreams
    xmlns="http://www.fedora.info/definitions/1/0/access/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.fedora.info/definitions/1/0/access/ http://www.fedora-commons.org/definitions/1/0/listDatastreams.xsd"
    pid="{pid}"
    baseURL="http://fakeurl/">
<datastream dsid="ERUDITXSD300" label="ERUDITXSD300" mimeType="text/xml"/>
<datastream dsid="UNIT" label="UNIT" mimeType="text/xml"/>
<datastream dsid="DC" label="Dublin Core Record for this object" mimeType="text/xml"/>
<datastream dsid="RELS-EXT" label="Relationships" mimeType="application/rdf+xml"/>
{extra}
</objectDatastreams>
"""  # noqa

FAKE_EMPTY_QUERY_RESULTS = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns="http://www.fedora.info/definitions/1/0/types/"><resultList></resultList></result>"""


class FakeResponse:
    def __init__(self, content, path):
        self.status_code = 200 if content else 404
        self.content = content
        self.url = FakeAPI.BASE_URL + path
        self.text = ""


class FakeAPI(ApiFacade):
    BASE_URL = 'http://fakeurl/'

    def __init__(self):
        super().__init__(self.BASE_URL, 'username', 'password')
        self._content_map = {}
        self._datastream_map = {}
        self._articles_with_pdf = set()
        self._query_results = {
            'series': set(),
            'publication': set(),
            'unit': set(),
        }

    def _make_request(self, reqmeth, url, *args, **kwargs):
        raise AssertionError()  # we should never get there in a testing environment

    def get_journal_xml(self, pid):
        if pid in self._content_map:
            content = self._content_map[pid]
            if content:
                return content
            else:
                # default fixture
                with open('./tests/fixtures/journal/minimal.xml', 'rb') as xml:
                    return xml.read()
        else:
            return None

    def get_publication_xml(self, pid):
        if pid in self._content_map:
            content = self._content_map[pid]
            if content:
                return content
            else:
                # default fixture
                with open('./tests/fixtures/issue/minimal.xml', 'rb') as xml:
                    return xml.read()
        else:
            return None

    def get_article_xml(self, pid):
        if pid in self._content_map:
            content = self._content_map[pid]
            if content:
                return content
            else:
                # default fixture
                with open('./tests/fixtures/article/009255ar.xml', 'rb') as xml:
                    return xml.read()
        else:
            return None

    def get_article_pdf(self, pid):
        if pid in self._articles_with_pdf:
            # default fixture
            with open('./tests/unit/apps/public/journal/fixtures/article.pdf', 'rb') as pdf:
                return pdf.read()
        else:
            return None

    def register_pid(self, pid, with_pdf=False):
        # tell the FakeAPI to return the default article fixture for pid. Same as set_article_xml(),
        # but for when you don't really care about the contents.
        if pid not in self._content_map:
            self._content_map[pid] = None
        if with_pdf:
            self._articles_with_pdf.add(pid)

    def register_datastream(self, pid, datastream_id, datastream_content):
        if not pid in self._datastream_map.keys():
            self._datastream_map[pid] = {}
        self._datastream_map[pid][datastream_id] = datastream_content

    register_publication = register_pid
    register_article = register_pid

    def add_pdf_to_article(self, pid):
        self._articles_with_pdf.add(pid)

    def set_xml_for_pid(self, pid, xml):
        if isinstance(xml, str):
            xml = xml.encode('utf-8')
        self._content_map[pid] = xml

    set_publication_xml = set_xml_for_pid
    set_article_xml = set_xml_for_pid

    @contextmanager
    def open_article(self, pid):
        # we implicitly register a pid that we tweak
        self.register_article(pid)
        xml = self.get_article_xml(pid)
        dom_wrapper = EruditArticleDomChanger(xml)
        yield dom_wrapper
        newxml = dom_wrapper.tostring()
        self.set_article_xml(pid, newxml)

    @contextmanager
    def open_publication(self, pid):
        # we implicitly register a pid that we tweak
        self.register_publication(pid)
        xml = self.get_publication_xml(pid)
        dom_wrapper = EruditPublicationDomChanger(xml)
        yield dom_wrapper
        newxml = dom_wrapper.tostring()
        self.set_publication_xml(pid, newxml)

    @contextmanager
    def open_journal(self, pid):
        # we implicitly register a pid that we tweak
        self.register_pid(pid)
        xml = self.get_journal_xml(pid)
        dom_wrapper = EruditJournalDomChanger(xml)
        yield dom_wrapper
        newxml = dom_wrapper.tostring()
        self.set_xml_for_pid(pid, newxml)

    def add_article_to_parent_publication(
            self, article, publication_allowed=True, pdf_url=None, html_url=None):
        with self.open_publication(article.issue.pid) as wrapper:
            wrapper.add_article(
                article,
                publication_allowed=publication_allowed,
                pdf_url=pdf_url,
                html_url=html_url)
            self._query_results['publication'].update({article.issue.pid})
            self._query_results['unit'].update({article.pid})

    def add_publication_to_parent_journal(self, issue, journal=None):
        if journal is None:
            journal = issue.journal
        with self.open_journal(journal.pid) as wrapper:
            wrapper.add_issue(issue)
            self._query_results['series'].update({journal.pid})
            self._query_results['publication'].update({issue.pid})

    def add_notes_to_journal(self, notes, journal):
        with self.open_journal(journal.pid) as wrapper:
            wrapper.add_notes(notes)

    def get(self, url, **kwargs):
        if url == 'objects':
            params = kwargs.get('params')
            query = params.get('query')
            label = re.search("label='([A-Za-z]+) Erudit'", query)
            if label:
                xml = etree.fromstring(FAKE_EMPTY_QUERY_RESULTS.encode('utf-8'))
                for pid in self._query_results.get(label.group(1).lower(), []):
                    xml.append(E.objectField(E.pid(pid)))
                return FakeResponse(etree.tostring(xml), url)
            return FakeResponse(FAKE_EMPTY_QUERY_RESULTS.encode('utf-8'), url)
        result = None
        pid = None
        m = re.match(r"^objects/(erudit:[\w\-.]+)(/datastreams)?(.*)", url)
        if m:
            pid, datastream, subselection = m.groups()
            prefix, subpid = pid.split(':')
            pidelems = subpid.split('.')
            if len(pidelems) == 4 and re.match('^p[0-9]+$', pidelems[3]):  # page
                if not subselection:  # we want a datastream list
                    result = FAKE_PAGE_DATASTREAM_LIST.format(pid=pid).encode()
                elif subselection == '/IMAGE/content':
                    with open('./tests/fixtures/page/{}.jpg'.format(pidelems[3]), 'rb') as page:
                        result = page.read()
            elif len(pidelems) == 4:  # article
                article_xml = self.get_article_xml(pid)
                if not article_xml:
                    # return empty response
                    result = b''
                elif not datastream:
                    # we're asking for the object profile
                    result = FAKE_FEDORA_PROFILE.format(
                        pid=pid, full_url=self.BASE_URL + url
                    ).encode()
                elif not subselection:  # we want a datastream list
                    if pid in self._articles_with_pdf:
                        extra = "<datastream dsid=\"PDF\" label=\"PDF\" mimeType=\"application/pdf\"/>"  # noqa
                    else:
                        extra = ""
                    result = FAKE_ARTICLE_DATASTREAM_LIST.format(pid=pid, extra=extra).encode()
                elif subselection == '/ERUDITXSD300/content':
                    result = self.get_article_xml(pid) or b''
                elif subselection == '/PDF/content':
                    result = self.get_article_pdf(pid) or None
            elif len(pidelems) == 3:  # issue
                if not datastream:
                    # we're asking for the object profile
                    result = FAKE_FEDORA_PROFILE.format(
                        pid=pid, full_url=self.BASE_URL + url
                    ).encode()
                elif not subselection:  # we want a datastream list
                    result = FAKE_ISSUE_DATASTREAM_LIST.format(pid=pid).encode()
                elif subselection == '/SUMMARY/content':
                    result = self.get_publication_xml(pid) or b''
                elif subselection == '/PAGES/content':
                    with open('./tests/fixtures/issue/datastream/pages/liberte03419.xml', 'rb') as xml:  # noqa
                        result = xml.read()
            elif len(pidelems) == 2:  # journal
                subselections = [
                    '/PUBLICATIONS/content',
                    '/OAISET_INFO/content',
                    '/RELS-EXT/content',
                ]
                if not datastream:
                    # we're asking for the object profile
                    result = FAKE_FEDORA_PROFILE.format(
                        pid=pid, full_url=self.BASE_URL + url
                    ).encode()
                elif not subselection:  # we want a datastream list
                    result = FAKE_JOURNAL_DATASTREAM_LIST.format(pid=pid).encode()

                elif pid in self._datastream_map.keys() and subselection in self._datastream_map[pid].keys():
                    result = self._datastream_map[pid][subselection]

                elif subselection in subselections:
                    result = self.get_journal_xml(pid) or b''
        if result is not None:
            response = FakeResponse(result, url)
            if response.status_code == 200:
                return response
            else:
                response.text = pid
                raise RequestFailed(response)
        else:
            print("WARNING: unsupported URL for fake fedora API: {}".format(url))
            response = FakeResponse(b'', url)
            response.text = pid
            raise RequestFailed(response)
