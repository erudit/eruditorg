from core.accounts.models import LegacyAccountProfile


def can_modify_account(user):
    if LegacyAccountProfile.objects.filter(
        user_id=user.id, origin=LegacyAccountProfile.DB_RESTRICTION
    ).count():
        return False
    return True
