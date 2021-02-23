# -*- coding: utf-8 -*-

import django.dispatch


userspace_post_transition = django.dispatch.Signal(
    providing_args=[
        "issue_submission",
        "transition_name",
        "request",
    ]
)
