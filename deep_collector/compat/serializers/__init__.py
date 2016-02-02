
import django


if django.VERSION < (1, 7):
    from .django_1_6 import *
else:
    from .django_1_7 import *
