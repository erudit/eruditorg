# -*- coding: utf-8 -*-

import rules

from erudit.models import Journal

from core.authorization.predicates import AuthorizationChecker
from core.authorization.defaults import AuthorizationConfig as AC

from .rules_helpers import get_editable_journals


@rules.predicate
def can_manage_a_journal(user):
    return is_journal_member(user) and AuthorizationChecker(
        [
            AC.can_edit_journal_information,
            AC.can_manage_authorizations,
            AC.can_manage_issuesubmission,
            AC.can_manage_individual_subscription,
        ]
    )


@rules.predicate
def is_journal_member(user, journal=None):
    if journal is None:
        return bool(Journal.objects.filter(members=user).count())
    else:
        return bool(journal.members.filter(id=user.id).count())


@rules.predicate
def can_edit_journal(user, journal=None):
    # TODO: add proper permissions checks
    if journal is None:
        return bool(get_editable_journals(user).count())
    else:
        return bool(journal.members.filter(id=user.id).count())
