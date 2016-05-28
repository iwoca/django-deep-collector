import django

if django.VERSION < (1, 7):
    from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
else:
    from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
