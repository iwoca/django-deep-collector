
from django.core.serializers.json import Serializer
from django.utils import six


class CustomizableLocalFieldsSerializer(Serializer):
    """
    This is a not so elegant copy/paste from django.core.serializer.base.Serializer serialize method.
    We wanted to add parent fields of current serialized object because they are lacking when we want to import them
    again.
    We had to redefine serialize() method to add the possibility to subclass methods that are getting local
    fields to serialize (get_local_fields and get_local_m2m_fields)
    """
    def serialize(self, queryset, **options):
        self.options = options

        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)

        self.start_serialization()
        self.first = True
        for obj in queryset:
            self.start_object(obj)
            # Use the concrete parent class' _meta instead of the object's _meta
            # This is to avoid local_fields problems for proxy models. Refs #17717.
            concrete_model = obj._meta.concrete_model
            for field in self.get_local_fields(concrete_model):
                if field.serialize:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in self.get_local_m2m_fields(concrete_model):
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()
        return self.getvalue()

    def get_local_fields(self, concrete_model):
        return concrete_model._meta.local_fields

    def get_local_m2m_fields(self, concrete_model):
        return concrete_model._meta.many_to_many
