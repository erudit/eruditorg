# -*- coding: utf-8 -*-

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .action_pool import actions
from .models import AccountActionToken
from .signals import action_token_consumed

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AccountActionToken)
def send_creation_notification_email(sender, instance, *args, **kwargs):
    created = kwargs.get('created')
    if created:
        action = actions.get_action(instance.action)
        if action:
            action.send_notification_email(instance)
        else:  # pragma: no cover
            logger.warning(
                'Unable to send a notification email because the configuration of '
                'the following action cannot be found: {}'.format(instance.action), exc_info=True)


@receiver(action_token_consumed)
def execute_action(sender, instance, consumer, **kwargs):
    action = actions.get_action(instance.action)
    if action:
        action.execute(instance)
    else:  # pragma: no cover
        logger.warning(
            'Unable to execute the action because the configuration of '
            'the following action cannot be found: {}'.format(instance.action), exc_info=True)
