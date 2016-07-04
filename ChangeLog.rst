ChangeLog
=========


.. _v0.4.2:

0.4.2 (2016-07-04)
------------------

*Bugfix:*

    - Fixing bug introduced in 0.4.1, related to inherited model collection. The django documentation was followed
      to help for compatibility_, but there is an issue related to inherited models and explained in this ticket_.

.. _compatibility: https://docs.djangoproject.com/en/1.9/ref/models/meta/
.. _ticket: https://code.djangoproject.com/ticket/25461


.. _v0.4.1:

0.4.1 (2016-06-29)
------------------

*New:*

    - Adding compat function to get related and related_m2m fields (_meta API updated in Django 1.9).


.. _v0.4:

0.4 (2016-06-19)
----------------

*New:*

    - Adding ``GenericForeignKey`` support.
    - Adding compat function to get local fields (_meta API updated in Django 1.9).


.. _v0.3.1:

0.3.1 (2016-04-06)
------------------

*New:*

    - Adding Django 1.9 compatibility.


.. _v0.3:


0.3 (2016-02-11)
----------------

*New:*

    - Adding python 3 compatibility.
    - Adding Django 1.8 compatibility.

*bugfix:*

    - Fixing collector bug when collecting a ``None`` child.


.. _v0.2.1:

0.2.1 (2016-02-03)
------------------

*bugfix:*

    - Fixing MANIFEST.in to include ``compat`` module, not added in distribution version (packaging was broken).


.. _v0.2:

0.2 (2016-02-02)
----------------

*New:*

    - Adding new ``compat`` module.
    - Now compatible with Django 1.7.x.


.. _v0.1.1:

0.1.1 (2015-09-23)
------------------

*New:*

    - Adding new ``get_report`` method to have collect detailed informations.
    - Various bug fixes


.. _v0.1:

0.1 (2015-04-21)
----------------

*New:*

    - Adding new ``RelatedObjectsCollector`` to collect every object that is related to given object.
    - Adding new ``MultiModelInheritanceSerializer`` to properly serialize collected item, to then be imported with Django `load_data` command.
