
from django.db import models
from django.conf import settings


class FKDummyModel(models.Model):
    name = models.CharField(max_length=255)


class O2ODummyModel(models.Model):
    name = models.CharField(max_length=255)


class BaseModel(models.Model):
    name = models.CharField(max_length=255)
    fkey = models.ForeignKey(FKDummyModel)
    o2o = models.OneToOneField(O2ODummyModel)


class ManyToManyToBaseModel(models.Model):
    name = models.CharField(max_length=255)
    m2m = models.ManyToManyField(BaseModel)


class ManyToManyToBaseModelWithRelatedName(models.Model):
    name = models.CharField(max_length=255)
    m2m = models.ManyToManyField(BaseModel, related_name='custom_related_m2m_name')


class ForeignKeyToBaseModel(models.Model):
    name = models.CharField(max_length=255)
    fkeyto = models.ForeignKey(BaseModel)


class OneToOneToBaseModel(models.Model):
    name = models.CharField(max_length=255)
    o2oto = models.OneToOneField(BaseModel)


class ClassLevel1(models.Model):
    name = models.CharField(max_length=255)


class ClassLevel2(models.Model):
    name = models.CharField(max_length=255)
    fkey = models.ForeignKey(ClassLevel1)


class ClassLevel3(models.Model):
    name = models.CharField(max_length=255)
    fkey = models.ForeignKey(ClassLevel2)


class ChildModel(BaseModel):
    child_field = models.CharField(max_length=255)
