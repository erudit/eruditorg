import rules
from rules.predicates import is_staff, is_superuser

from core.permissions.predicates import HasObjectPermission
from erudit.rules import is_journal_member

MANAGE_PERMISSION = "manage_permissions"

# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    'userspace.manage_permissions',
    is_superuser | is_staff |
    is_journal_member & HasObjectPermission(MANAGE_PERMISSION)
)
