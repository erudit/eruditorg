import rules
from rules.predicates import is_superuser, is_staff

from core.permissions.predicates import HasPermission
from erudit.rules import is_journal_member

# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    'editor.manage_issuesubmission',
    is_superuser | is_staff |
    is_journal_member & HasPermission("editor.manage_issuesubmission"),
)

rules.add_perm(
    'editor.review_issuesubmission',
    is_superuser | is_staff |
    is_journal_member & HasPermission("editor.review_issuesubmission"),
)
