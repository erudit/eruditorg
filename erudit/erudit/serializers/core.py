# -*- coding: utf-8 -*-

from rest_framework import serializers

from .. import models as erudit_models


class EruditDocumentSerializer(serializers.ModelSerializer):
    real_object = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.EruditDocument
        fields = ['localidentifier', 'real_object', ]

    def get_real_object(self, obj):
        # This method should return a serialized representation of an Érudit document ; it could be
        # an article, a thesis, a book, ...
        # However there is a problem: it not currently possible to determine the correct model
        # associated with an EruditDocument instance. For now we use only Article objects so we
        # will make the assumption that all Érudit documents are article... But this problem should
        # be resolved using polymorphism.
        article = erudit_models.Article.objects.get(id=obj.id)
        return ArticleSerializer(article).data


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = erudit_models.Article
        fields = ['title', 'surtitle', 'processing', ]
