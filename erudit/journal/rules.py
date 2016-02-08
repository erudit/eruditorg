# -*- coding: utf-8 -*-

import rules

from userspace.rules import is_staff
from userspace.rules import is_superuser

from .rules_helpers import get_editable_journals


@rules.predicate
def can_edit_journal(user, journal=None):
    # TODO: add proper permissions checks
    if journal is None:
        return bool(get_editable_journals(user).count())
    else:
        return bool(journal.members.filter(id=user.id).count())


rules.add_perm('journal.edit_journal',
               is_superuser | is_staff | can_edit_journal)
