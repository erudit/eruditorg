# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from .models import Journal


@rules.predicate
def is_journal_member(user, journal=None):
    if journal is None:
        return bool(Journal.objects.filter(members=user).count())
    else:
        return bool(journal.members.filter(id=user.id).count())


rules.add_perm('erudit.manage_journal',
               is_authenticated & (is_superuser | is_staff | is_journal_member))
