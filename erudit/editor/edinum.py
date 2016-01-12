import logging
from datetime import datetime

import pymysql

from django.conf import settings

from erudit.models import Publisher, Journal

EDINUM_SQL_QUERY = """
SELECT c.PersonID, ap.Name, cs.SeriesID, t.id as journal_id, t.name, sp.shortname, t.Subtitle
FROM edinum.contributionseries cs
JOIN title t ON cs.SeriesID = t.SeriesID
JOIN contribution c ON cs.ContributionID = c.ID
JOIN artificialperson ap ON c.PersonID = ap.PersonID
JOIN seriesproduction sp ON t.SeriesId = sp.SeriesID
WHERE ContributiontypeID = '3';"""  # noqa

log = logging.getLogger(__name__)


def fetch_publishers_from_edinum():
    edinum = settings.EXTERNAL_DATABASES['edinum']

    conn = pymysql.connect(
        host=edinum['HOST'],
        unix_socket='/tmp/mysql.sock',
        user=edinum['USER'],
        passwd=edinum['PASSWORD'],
        db=edinum['NAME'],
    )

    cur = conn.cursor()
    cur.execute(EDINUM_SQL_QUERY)
    return cur.fetchall()


def create_or_update_journal(
        publisher, journal_id, journal_name, journal_shortname, journal_subtitle):
    journal_count = Journal.objects.filter(
        edinum_id=journal_id
    ).count()

    if journal_count > 1:
        error = "There should be only one journal with id {}. Not updating"  # noqa
        log.error({"msg": error.format(journal_id)})
        return None

    elif journal_count == 1:
        journal = Journal.objects.get(edinum_id=journal_id)

        if not journal.synced_with_edinum:
            warn = "Found a journal with id {}. However, it is not synced with edinum. Not updating"  # noqa
            log.warn({"msg": warn.format(journal_id)})
            return None
        else:
            journal.publisher = publisher
            journal.name = journal_name
            journal.code = journal_shortname
            journal.subtitle = journal_subtitle
            journal.sync_date = datetime.now()
            journal.save()
            return journal
    else:
        journal = Journal(
            name=journal_name,
            code=journal_shortname,
            subtitle=journal_subtitle,
            synced_with_edinum=True,
            edinum_id=journal_id,
            publisher=publisher,
            sync_date=datetime.now(),
        )

        journal.save()
        return journal


def create_or_update_publisher(person_id, publisher_name):

    publisher_count = Publisher.objects.filter(
        edinum_id=person_id
    ).count()

    if publisher_count > 1:
        error_msg = "There should be only one publisher with id {}. Not updating".format(  # noqa
            person_id
        )

        log.error({"msg": error_msg})
        return None

    elif publisher_count == 1:
        publisher = Publisher.objects.get(edinum_id=person_id)

        if not publisher.synced_with_edinum:
            warn = "Found a publisher with id {}. However, it is not synced with edinum. Not updating"  # noqa
            log.warn({"msg": warn.format(person_id)})
            return None
        else:
            publisher.name = publisher_name
            publisher.sync_date = datetime.now()
            publisher.save()
            return publisher
    else:
        publisher = Publisher(
            name=publisher_name,
            synced_with_edinum=True,
            edinum_id=person_id,
            sync_date=datetime.now(),
        )
        publisher.save()

        return publisher
