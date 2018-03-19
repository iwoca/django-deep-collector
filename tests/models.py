
from django.contrib.contenttypes.models import ContentType
from django.db import models

from deep_collector.compat.fields import GenericForeignKey, GenericRelation


class FKDummyModel(models.Model):
    name = models.CharField(max_length=255)


class O2ODummyModel(models.Model):
    name = models.CharField(max_length=255)


class BaseModel(models.Model):
    name = models.CharField(max_length=255)
    fkey = models.ForeignKey(FKDummyModel, on_delete=models.CASCADE)
    o2o = models.OneToOneField(O2ODummyModel, on_delete=models.CASCADE)


class SubClassOfBaseModel(BaseModel):
    pass


class ManyToManyToBaseModel(models.Model):
    name = models.CharField(max_length=255)
    m2m = models.ManyToManyField(BaseModel)


class ManyToManyToBaseModelWithRelatedName(models.Model):
    name = models.CharField(max_length=255)
    m2m = models.ManyToManyField(BaseModel, related_name='custom_related_m2m_name')


class ForeignKeyToBaseModel(models.Model):
    name = models.CharField(max_length=255)
    fkeyto = models.ForeignKey(BaseModel, on_delete=models.CASCADE)


class OneToOneToBaseModel(models.Model):
    name = models.CharField(max_length=255)
    o2oto = models.OneToOneField(BaseModel, on_delete=models.CASCADE)


class ClassLevel1(models.Model):
    name = models.CharField(max_length=255)


class ClassLevel2(models.Model):
    name = models.CharField(max_length=255)
    fkey = models.ForeignKey(ClassLevel1, on_delete=models.CASCADE)


class ClassLevel3(models.Model):
    name = models.CharField(max_length=255)
    fkey = models.ForeignKey(ClassLevel2, on_delete=models.CASCADE)


class ChildModel(BaseModel):
    child_field = models.CharField(max_length=255)


class InvalidFKRootModel(models.Model):
    valid_fk = models.ForeignKey('InvalidFKNonRootModel', related_name='valid_non_root_fk', null=True, on_delete=models.CASCADE)
    invalid_fk = models.ForeignKey('InvalidFKNonRootModel', related_name='invalid_non_root_fk', null=True, on_delete=models.CASCADE)


class InvalidFKNonRootModel(models.Model):
    valid_fk = models.ForeignKey(InvalidFKRootModel, related_name='valid_root_fk', null=True, on_delete=models.CASCADE)
    invalid_fk = models.ForeignKey(InvalidFKRootModel, related_name='invalid_root_fk', null=True, on_delete=models.CASCADE)


class GFKModel(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class BaseToGFKModel(models.Model):
    gfk_relation = GenericRelation(GFKModel)
