
from StringIO import StringIO
from django.core.serializers.json import Serializer



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

        self.stream = options.pop("stream", StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)

        self.start_serialization()
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
        self.end_serialization()
        return self.getvalue()

    def get_local_fields(self, concrete_model):
        return concrete_model._meta.local_fields

    def get_local_m2m_fields(self, concrete_model):
        return concrete_model._meta.many_to_many


class MultiModelInheritanceSerializer(CustomizableLocalFieldsSerializer):
    '''
    This serializer aims to fix serialization for multi-model inheritance
    This functionality has been removed because considered as too much "agressive"
    More precisions on this commit: https://github.com/django/django/commit/12716794db

    '''
    def get_local_fields(self, concrete_model):
        local_fields = super(MultiModelInheritanceSerializer, self).get_local_fields(concrete_model)
        return local_fields + self.parent_local_fields

    def get_local_m2m_fields(self, concrete_model):
        local_m2m_fields = super(MultiModelInheritanceSerializer, self).get_local_m2m_fields(concrete_model)
        return local_m2m_fields + self.parent_local_m2m_fields

    def start_object(self, obj):
        # Initializing local fields we want to add current object (will be parent local fields)
        self.parent_local_fields = []
        self.parent_local_m2m_fields = []

        # Recursively getting parent fields to be added to serialization
        # We use concrete_model to avoid problems if we have to deal with proxy models
        concrete_model = obj._meta.concrete_model
        self.collect_parent_fields(concrete_model)

        super(Serializer, self).start_object(obj)

    def collect_parent_fields(self, model):
        # Collect parent fields that are not collected by default on non-abstract models. We call it recursively
        # to manage parents of parents, ...
        parents = model._meta.parents
        parents_to_collect = [parent for parent, parent_ptr in parents.iteritems() if not parent._meta.abstract]

        for parent in parents_to_collect:
            self.parent_local_fields += parent._meta.local_fields
            self.parent_local_m2m_fields += parent._meta.local_many_to_many

            self.collect_parent_fields(parent._meta.concrete_model)
