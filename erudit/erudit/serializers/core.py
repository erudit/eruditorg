# -*- coding: utf-8 -*-

from rest_framework import serializers

from .. import models as erudit_models


class EruditDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = erudit_models.EruditDocument
        fields = ['id', 'localidentifier', ]
