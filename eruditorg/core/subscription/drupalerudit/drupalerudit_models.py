# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify,
#     and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Authmap(models.Model):
    aid = models.AutoField(primary_key=True)
    uid = models.IntegerField()
    authname = models.CharField(unique=True, max_length=128)
    module = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'authmap'
        app_label = 'drupalerudit'


class Role(models.Model):
    rid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=64)
    weight = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'role'
        app_label = 'drupalerudit'


class Sessions(models.Model):
    uid = models.IntegerField()
    sid = models.CharField(max_length=128)
    ssid = models.CharField(max_length=128)
    hostname = models.CharField(max_length=128)
    timestamp = models.IntegerField()
    cache = models.IntegerField()
    session = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sessions'
        unique_together = (('sid', 'ssid'),)
        app_label = 'drupalerudit'


class Users(models.Model):
    uid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=60)
    pass_field = models.CharField(db_column='pass', max_length=128)
    mail = models.CharField(max_length=254, blank=True, null=True)
    theme = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    signature_format = models.CharField(max_length=255, blank=True, null=True)
    created = models.IntegerField()
    access = models.IntegerField()
    login = models.IntegerField()
    status = models.IntegerField()
    timezone = models.CharField(max_length=32, blank=True, null=True)
    language = models.CharField(max_length=12)
    picture = models.IntegerField()
    init = models.CharField(max_length=254, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    uuid = models.CharField(max_length=36)

    class Meta:
        managed = False
        db_table = 'users'
        app_label = 'drupalerudit'


class UsersRoles(models.Model):
    uid = models.IntegerField()
    rid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'users_roles'
        unique_together = (('uid', 'rid'),)
        app_label = 'drupalerudit'
