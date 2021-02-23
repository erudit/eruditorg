# -*- coding: utf-8 -*-

from django.http import JsonResponse


def JsonAckResponse(**kwargs):
    """ Returns a JsonResponse that acknowledges the success of an operation. """
    json_dict = {"status": "ok"}
    json_dict.update(kwargs)
    return JsonResponse(json_dict)


def JsonErrorResponse(error, **kwargs):
    """ Returns a JsonResponse that notifies an error that occured during an operation. """
    json_dict = {"status": "nok", "error": error}
    json_dict.update(kwargs)
    return JsonResponse(json_dict)
