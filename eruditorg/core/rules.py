import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser


# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    'staff_access',
    is_authenticated & (
        is_superuser | is_staff
    ),
)
