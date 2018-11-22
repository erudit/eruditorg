import structlog
import lxml.etree as et

from .repository import api
from .objects import JournalDigitalObject
from eruditarticle.utils import remove_xml_namespaces


logger = structlog.getLogger(__name__)


def get_pids(query):
    """ Returns the PIDS corresponding to a given Fedora query. """
    ns_type = {'type': 'http://www.fedora.info/definitions/1/0/types/'}
    pids = []
    session_token = None
    remaining_pids = True

    while remaining_pids:
        # The session token is used by the Fedora Commons repository to paginate a list of
        # results. We have to use it in order to construct the list of PIDs to import!
        session_token = session_token.text if session_token is not None else None
        response = api.findObjects(query, chunksize=1000, session_token=session_token)
        # Tries to fetch the PIDs by parsing the response
        tree = et.fromstring(response.content)
        pid_nodes = tree.findall('.//type:pid', ns_type)
        session_token = tree.find('./type:listSession//type:token', ns_type)
        _pids = [n.text for n in pid_nodes]
        pids.extend(_pids)

        remaining_pids = len(_pids) and session_token is not None

    return pids


def is_issue_published_in_fedora(issue_pid, journal=None, journal_pid=None):
    """ Returns true if an issue is published """
    try:
        if journal:
            journal_pid = journal.pid
        fedora_journal = JournalDigitalObject(api, journal_pid)
        assert fedora_journal.exists
    except AssertionError:
        logger.error("journal.DoesNotExist", pid=journal.pid)
        return False
    else:
        publications_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.publications.content.serialize()))
        xml_issue_nodes = publications_tree.findall('.//numero')
        for issue_node in xml_issue_nodes:
            if issue_node.get('pid') == issue_pid:
                return True
    return False


def get_unimported_issues_pids(include_unpublished_issues=False):
    from erudit.models import Issue

    issue_fedora_query = "pid~erudit:erudit.*.* label='Publication Erudit'"
    issue_pids = get_pids(issue_fedora_query)

    missing_issues = []
    for issue_pid in issue_pids:
        pid_parts = issue_pid.split('.')
        issue_localidentifier = pid_parts[-1]

        journal_pid = ".".join(pid_parts[:len(pid_parts) - 1])
        try:
            Issue.objects.get(localidentifier=issue_localidentifier)
        except Issue.DoesNotExist:
            is_published = is_issue_published_in_fedora(issue_pid, journal_pid=journal_pid)
            if is_published or (not is_issue_published_in_fedora and include_unpublished_issues):  # noqa
                missing_issues.append(issue_pid)
                logger.info("issue.unimported", pid=issue_pid, published_in_fedora=is_published)
    return missing_issues


def localidentifier_from_pid(pid):
    """ erudit:erudit.ae49.ae03128 --> ae03128 """
    return pid.split(".")[-1]
