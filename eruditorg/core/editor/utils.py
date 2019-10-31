import datetime as dt

from core.editor.conf import settings as editor_settings


def get_archive_date(validation_date):
    return validation_date + dt.timedelta(days=editor_settings.ARCHIVAL_DAY_OFFSET)
