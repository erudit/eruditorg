import rules

from userspace.rules import is_superuser, is_staff

from erudit.models import Journal
from erudit.rules import can_manage_journal


@rules.predicate
def can_manage_issuesubmission(user, issue=None):
    if issue is None:
        return bool(Journal.objects.filter(members=user).count())
    else:
        return can_manage_journal(user, issue.journal)


rules.add_perm('editor.manage_issuesubmission',
               is_superuser | is_staff | can_manage_issuesubmission)
