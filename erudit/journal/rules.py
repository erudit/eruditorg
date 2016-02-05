# -*- coding: utf-8 -*-

import rules

from erudit.models import Journal
from userspace.rules import is_staff
from userspace.rules import is_superuser


@rules.predicate
def can_edit_journal(user, journal=None):
    if journal is None:
        return bool(Journal.objects.filter(members=user).count())
    else:
        return bool(journal.members.filter(id=user.id).count())


rules.add_perm('erudit.edit_journal',
               is_superuser | is_staff | can_edit_journal)
