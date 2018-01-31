from core.accounts.models import LegacyAccountProfile


def can_modify_account(user):
    if LegacyAccountProfile.objects.filter(
        user=user,
        origin=LegacyAccountProfile.DB_RESTRICTION
    ).count():
        return False
    return True
