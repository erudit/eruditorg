import rules

from core.userspace.rules import is_superuser, is_staff

from .models import Journal


@rules.predicate
def can_manage_journal(user, journal=None):
    if journal is None:
        return bool(Journal.objects.filter(members=user).count())
    else:
        return bool(journal.members.filter(id=user.id).count())


rules.add_perm('erudit.manage_journal',
               is_superuser | is_staff | can_manage_journal)
