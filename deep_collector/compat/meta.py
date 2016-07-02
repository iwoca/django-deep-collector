import django

if django.VERSION < (1, 8):
    def get_all_related_objects(obj):
        return obj._meta.get_all_related_objects()

    def get_all_related_m2m_objects_with_model(obj):
        return obj._meta.get_all_related_m2m_objects_with_model()

    def get_compat_local_fields(obj):
        # virtual_fields are used to collect GenericForeignKey objects
        return obj._meta.local_fields + obj._meta.virtual_fields
else:
    def get_all_related_objects(obj):
        return  [
            f for f in obj._meta.get_fields()
            if (f.one_to_many or f.one_to_one) and 
               f.auto_created and not f.concrete
        ]

    def get_all_related_m2m_objects_with_model(obj):
        return  [
            (f, f.model if f.model != obj.__class__ else None)
            for f in obj._meta.get_fields(include_hidden=True)
            if f.many_to_many and f.auto_created
        ]

    def get_compat_local_fields(obj):
        return obj._meta.get_fields()
