import logging
import lxml.etree as et

from eulfedora.util import RequestFailed
from .repository import rest_api

logger = logging.getLogger(__name__)

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
        try:
            response = rest_api.findObjects(query, chunksize=1000, session_token=session_token)
            # Tries to fetch the PIDs by parsing the response
            tree = et.fromstring(response.content)
            pid_nodes = tree.findall('.//type:pid', ns_type)
            session_token = tree.find('./type:listSession//type:token', ns_type)
            _pids = [n.text for n in pid_nodes]
        except RequestFailed as e:
            logger.info('[FAIL]')
            return
        else:
            pids.extend(_pids)

        remaining_pids = len(_pids) and session_token is not None

    logger.info('[OK]')
    if not len(pids):
        logger.info('No PIDs found')
    else:
        logger.info('  {0} PIDs found!'.format(len(pids)))

    return pids

