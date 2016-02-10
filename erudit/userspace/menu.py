from django.utils.translation import ugettext_lazy as _

from navutils import menu


main_menu = menu.Menu('main')
menu.register(main_menu)

userspace = menu.Node(
    id='userspace',
    label=_('Mon espace'),
    pattern_name='userspace:dashboard',
)
main_menu.register(userspace)

journal = menu.AnyPermissionsNode(
    id='journal',
    label=_('Information de la revue'),
    pattern_name='journal:journal-information',
    permissions=['journal.edit_journal', ],
)

editor = menu.AnyPermissionsNode(
    id='editor',
    label=_('Dépôts de numéros'),
    pattern_name='editor:issues',
    permissions=['editor.manage_issuesubmission', ],
)

permissions = menu.AnyPermissionsNode(
    id='permissions',
    label=_('Permissions'),
    pattern_name='userspace:perm_list',
    permissions=['userspace.manage_permissions', ],
)

individual_subscription = menu.AnyPermissionsNode(
    id='individual_subscription',
    label=_('Abonnements individuels'),
    pattern_name='individual_subscription:account_list',
    permissions=['individual_subscription.manage_account', ],
)

userspace.children.append(journal)
userspace.children.append(editor)
userspace.children.append(permissions)
userspace.children.append(individual_subscription)
