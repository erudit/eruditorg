import re

from eulfedora.api import ApiFacade

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
</objectDatastreams>
""" # noqa


class FakeResponse:
    def __init__(self, content, path):
        self.content = content
        self.url = FakeAPI.BASE_URL + path


class FakeAPI(ApiFacade):
    BASE_URL = 'http://fakeurl/'

    def __init__(self):
        super().__init__(self.BASE_URL, 'username', 'password')

    def _make_request(self, reqmeth, url, *args, **kwargs):
        raise AssertionError()  # we should never get there in a testing environment

    def get(self, url, **kwargs):
        result = None
        m = re.match(r"^objects/(erudit:[\w\-.]+)(/datastreams)?(.*)", url)
        if m:
            pid, datastream, subselection = m.groups()
            prefix, subpid = pid.split(':')
            pidelems = subpid.split('.')
            if not datastream:
                # we're asking for the object profile
                result = FAKE_FEDORA_PROFILE.format(
                    pid=pid, full_url=self.BASE_URL + url
                ).encode()
            elif len(pidelems) == 4:  # article
                if not subselection:  # we want a datastream list
                    result = FAKE_ARTICLE_DATASTREAM_LIST.format(pid=pid).encode()
                elif subselection == '/ERUDITXSD300/content':
                    with open('./tests/fixtures/article/009255ar.xml', 'rb') as xml:
                        result = xml.read()
            elif len(pidelems) == 3:  # issue
                if not subselection:  # we want a datastream list
                    result = FAKE_ISSUE_DATASTREAM_LIST.format(pid=pid).encode()
                elif subselection == '/SUMMARY/content':
                    with open('./tests/fixtures/issue/liberte1035607.xml', 'rb') as xml:
                        result = xml.read()
            elif len(pidelems) == 2:  # journal
                if not subselection:  # we want a datastream list
                    result = FAKE_JOURNAL_DATASTREAM_LIST.format(pid=pid).encode()
                elif subselection == '/PUBLICATIONS/content':
                    with open('./tests/fixtures/journal/mi115.xml', 'rb') as xml:
                        result = xml.read()
        if result is not None:
            return FakeResponse(result, url)
        else:
            raise ValueError("unsupported URL for fake fedora API: {}".format(url))
