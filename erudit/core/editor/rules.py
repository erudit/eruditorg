import rules
from rules.predicates import is_superuser, is_staff

from core.permissions.predicates import HasObjectPermission
from erudit.rules import is_journal_member

MANAGE_ISSUESUBMISSION = "manage_issuesubmission"
REVIEW_ISSUESUBMISSION = "review_issuesubmission"

# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    'editor.manage_issuesubmission',
    is_superuser | is_staff |
    is_journal_member & HasObjectPermission(MANAGE_ISSUESUBMISSION),
)

rules.add_perm(
    'editor.review_issuesubmission',
    is_superuser | is_staff |
    is_journal_member & HasObjectPermission(REVIEW_ISSUESUBMISSION),
)
