# -*- coding: utf-8 -*-

import django.dispatch


action_token_consumed = django.dispatch.Signal(providing_args=['instance', 'consumer', ])
