import re

from django.contrib.auth import get_user_model

User = get_user_model()


def generate_unique_username(fullname):
    """ Generates a unique username from a fullname """

    fullname = re.sub("-", " ", fullname)
    names = fullname.split()

    parts = [
        n[0] for n in names[:len(names) - 1]
    ]

    username = "{first_name_letter}{other_names}".format(
        first_name_letter="".join(parts),
        other_names="".join(names[len(names) - 1])
    ).lower()

    username_count = User.objects.filter(
        username__startswith=username
    ).count()

    if username_count > 0:
        return "{username}{count}".format(
            username=username,
            count=username_count + 1
        )

    return username
