import datetime as dt
from core.editor.utils import get_archive_date


def test_can_calculate_archive_date():
    from core.editor.conf import settings as editor_settings

    editor_settings.ARCHIVE_DAY_OFFSETS = 1
    now = dt.datetime.now()
    assert get_archive_date(now) == now + dt.timedelta(editor_settings.ARCHIVAL_DAY_OFFSET)
