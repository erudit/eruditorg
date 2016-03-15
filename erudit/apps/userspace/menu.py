from django.utils.translation import ugettext_lazy as _

from navutils import menu

main_menu = menu.Menu('main')
menu.register(main_menu)

userspace = menu.Node(
    id='userspace',
    label=_('Mon espace'),
    pattern_name='userspace:dashboard',
    context={'icon': 'ion-ios-home-outline'},
)
main_menu.register(userspace)

journal = menu.AnyPermissionsNode(
    id='journal',
    label=_('Information de la revue'),
    pattern_name='userspace:journal:information:update',
    permissions=['journal.edit_journal', ],
    context={'icon': 'ion-ios-book-outline'},
)

editor = menu.AnyPermissionsNode(
    id='editor',
    label=_('Dépôts de numéros'),
    pattern_name='userspace:journal:editor:issues',
    permissions=['editor.manage_issuesubmission', ],
    context={'icon': 'ion-ios-copy-outline'},
)

authorization = menu.AnyPermissionsNode(
    id='autorisation',
    label=_('Autorisations'),
    pattern_name='userspace:journal:authorization:list',
    permissions=['authorization.manage_authorizations', ],
    context={'icon': 'ion-ios-locked-outline'},
)

subscription = menu.AnyPermissionsNode(
    id='subscription',
    label=_('Abonnements individuels'),
    pattern_name='userspace:journal:subscription:account_list',
    permissions=['subscription.manage_account', ],
    context={'icon': 'ion-ios-people-outline'},
)

userspace.children.append(journal)
userspace.children.append(editor)
userspace.children.append(authorization)
userspace.children.append(subscription)
