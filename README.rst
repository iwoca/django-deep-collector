==============
Deep Collector
==============

.. image:: https://travis-ci.org/iwoca/django-deep-collector.svg?branch=master
    :target: https://travis-ci.org/iwoca/django-deep-collector.svg

Django custom collector used to get every objects that are related to given object.

Install
=======

::

    $ pip install django-deep-collector


Usage
=====

Create a new instance of DeepCollector, and launch collector on one object:

.. code-block:: python

    from deep_collector.core import DeepCollector
    from django.contrib.auth.models import User

    user = User.objects.all()[0]
    collector = DeepCollector()
    collector.collect(user)
    related_objects = collector.get_collected_objects()

If you want to save it in a file to be 'django load_data'-like imported, you can use:

.. code-block:: python

    string_buffer = collector.get_json_serialized_objects()


How it works
============

This class is used to introspect an object, to get every other objects that depend on it, following its
'relation' fields, i.e. ForeignKey, OneToOneField, ManyToManyField, GenericForeignKey and GenericRelation.

1. We start from given object (of class classA for example), and loop over :

- Its 'direct' fields, it means the relation fields that are explicitly declared in this django model.

.. code-block:: python

    class classA(models.Model):
        fkey = models.ForeignKey(classB)
        o2o = models.OneToOneField(classC)
        m2m = models.ManyToManyField(classD)


- Its 'related' fields, so other django model that are related to this object by relation fields.

.. code-block:: python

    class classB(models.Model):
        fkeyto = models.ForeignKey(classA)

    class classC(models.Model):
        o2oto = models.OneToOneField(classA)

    class classD(models.Model):
        m2mto = models.ManyToManyField(classA)


2. For every field, we get associated object(s) of objA:

- If it's a direct field, we get objects by:

.. code-block:: python

    class classA(models.Model):
        fkey = models.ForeignKey(classB)        # objA.fkey
        o2o = models.OneToOneField(classC)      # objA.o2o
        m2m = models.ManyToManyField(classD)    # objA.m2m.all()


- If it's a related field, we get objects by:

.. code-block:: python

    class classB(models.Model):
        fkeyto = models.ForeignKey(classA)      # objA.classb_set.all()

    class classC(models.Model):
        o2oto = models.OneToOneField(classA)    # objA.classC (not a manager, because OneToOneField is a unique rel)

    class classD(models.Model):
        m2mto = models.ManyToManyField(classA)  # objA.classd_set.all()


If we are using related_name attribute, then we access manager with its related_name:

.. code-block:: python

    class classE(models.Model):
        m2mto = models.ForeignKey(classA, related_name='classE')  # objA.classE.all()

3. For each associated object, we go back to step 1. and get every field, ...


GenericForeignKey
=================

The `GenericForeignKey` has a small exception. If you want it to be collected in the "reverse" way, you should
explicitly define a `GenericRelation` in the models you want to follow this "reverse" relation.

.. code-block:: python

    class GFKModel(models.Model):
        content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
        object_id = models.PositiveIntegerField()
        content_object = GenericForeignKey('content_type', 'object_id')


    class BaseToGFKModel(models.Model):
        gfk_relation = GenericRelation(GFKModel)

In above example, if you collect a `BaseToGFKModel` instance, the collector will look for all `GFKModel` instances
related to your initial `BaseToGFKModel` instance.
That happens because the `BaseToGFKModel` model explicitly defines a `GenericRelation`.


Parameters
==========

You can customize which model/field is collected.
By default, every model and field is collected, but you can override some parameters to have custom behaviour:

- `EXCLUDE_MODELS`: exclude models (expecting a list of '<app_label>.<module_name>')

.. code-block:: python

    EXCLUDE_MODELS = ['sites.site', 'auth.permission', 'auth.group']

Every time we will try to collect an object of this model type, it won't be collected.

- `EXCLUDE_DIRECT_FIELDS`: exclude direct fields from specified models

.. code-block:: python

    EXCLUDE_DIRECT_FIELDS = {
        'auth.user': ['groups'],
    }

On User model, when we will get direct fields, we won't take into account 'groups' field.

- `EXCLUDE_RELATED_FIELDS`: exclude related fields from specified models

.. code-block:: python

    EXCLUDE_RELATED_FIELDS = {
        'auth.user': ['session_set']
    }

On User model, we don't want to collect sessions that are associated to this user, so we put the exact accessor name we have to use to get these sessions, 'session_set', to exclude them from collection.

- `ALLOWS_SAME_TYPE_AS_ROOT_COLLECT`: avoid by default to collect objects that have the same type as the root one, to prevent collecting too many data.

Miscellaneous
=============

To avoid some recursive collect between 2 objects (if an object has a direct field to another one, it means that other object has a related field to this first one), we detect if an object has already been collected before trying to collect it.
