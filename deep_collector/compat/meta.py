import django

if django.VERSION < (1, 8):
    def get_compat_local_fields(obj):
        # virtual_fields are used to collect GenericForeignKey objects
        return obj._meta.local_fields + obj._meta.virtual_fields
else:
    def get_compat_local_fields(obj):
        return obj._meta.get_fields()
