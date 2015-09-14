from django.db import models
from erudit import models as e


class Indexer(models.Model):
    pass

class Indexation(models.Model):

    journal
    indexer
