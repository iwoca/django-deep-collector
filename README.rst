=====
Deep Collector
=====
.. image:: https://travis-ci.org/iwoca/django-deep-collector.svg?branch=master
    :target: https://travis-ci.org/iwoca/django-deep-collector.svg

Django custom collector used to get every objects that are related to given object.

Usage
=====

Create a new instance of RelatedObjectsCollector, and launch collector on one object:

::

    >>> from deep_collector import RelatedObjectsCollector
    >>>
    >>> user = User.objects.all()[0]
    >>> collector = RelatedObjectsCollector()
    >>> collector.collect(user)
    >>> related_objects = collector.get_all_related_objects()

If you want to save it in a file to be 'django load_data'-like imported, you can use (only Django 1.4 supported for now):

::

    >>> string_buffer = collector.get_json_serialized_objects()


How it works
============

This class is used to introspect an object, to get every other objects that depend on it, following its
'relation' fields, i.e. ForeignKey, OneToOneField and ManyToManyField.

1. We start from given object (of class classA for example), and loop over :

- Its 'direct' fields, it means the relation fields that are explicitly declared in this django model.

::

    >>> class classA(models.Model):
    >>>     fkey = models.ForeignKey(classB)
    >>>     o2o = models.OneToOneField(classC)
    >>>     m2m = models.ManyToManyField(classD)


- Its 'related' fields, so other django model that are related to this object by relation fields.

::

    >>> class classB(models.Model):
    >>>     fkeyto = models.ForeignKey(classA)
    >>>
    >>> class classC(models.Model):
    >>>     o2oto = models.OneToOneField(classA)
    >>>
    >>> class classD(models.Model):
    >>>     m2mto = models.ManyToManyField(classA)


2. For every field, we get associated object(s) of objA:

- If it's a direct field, we get objects by:

::

    >>> class classA(models.Model):
    >>>     fkey = models.ForeignKey(classB)        # objA.fkey
    >>>     o2o = models.OneToOneField(classC)      # objA.o2o
    >>>     m2m = models.ManyToManyField(classD)    # objA.m2m.all()


- If it's a related field, we get objects by:

::

    >>> class classB(models.Model):
    >>>     fkeyto = models.ForeignKey(classA)      # objA.classb_set.all()
    >>>
    >>> class classC(models.Model):
    >>>     o2oto = models.OneToOneField(classA)    # objA.classC (not a manager, because OneToOneField is a unique rel)
    >>>
    >>> class classD(models.Model):
    >>>     m2mto = models.ManyToManyField(classA)  # objA.classd_set.all()


If we are using related_name attribute, then we access manager with its related_name:

::

    >>> class classE(models.Model):
    >>>     m2mto = models.ForeignKey(classA, related_name='classE')  # objA.classE.all()


3. For each associated object, we go back to step 1. and get every field, ...

Parameters
==========

You can customize which model/field is collected.
By default, every model and field is collected, but you can override some parameters to have custom behaviour:

- `EXCLUDE_MODELS`: exclude models (expecting a list of '<app_label>.<module_name>')

::

    >>> EXCLUDE_MODELS = ['sites.site', 'auth.permission', 'auth.group']
Every time we will try to collect an object of this model type, it won't be collected.

- `EXCLUDE_DIRECT_FIELDS`: exclude direct fields from specified models

::

    >>> EXCLUDE_DIRECT_FIELDS = {
            'auth.user': ['groups'],
        }
On User model, when we will get direct fields, we won't take into account 'groups' field.

- `EXCLUDE_RELATED_FIELDS`: exclude related fields from specified models

::

    >>> EXCLUDE_RELATED_FIELDS = {
            'auth.user': ['session_set']
        }
On User model, we don't want to collect sessions that are associated to this user, so we put the exact accessor
 name we have to use to get these session, 'session_set', to exclude it from collecting.


Miscellaneous
=============

To avoid some recursive collect between 2 objects (if an object has a direct field to another one, it means that other object has a related field to this first one), we detect if an object has already been collected before trying to collect it.

We are also avoiding by default to collect objects that have the same type as the root one, to prevent collecting too many data.
This behaviour can be changed with `ALLOWS_SAME_TYPE_AS_ROOT_COLLECT` parameter.
