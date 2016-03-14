
import django


if django.VERSION < (1, 7):
    from .django_1_6 import CustomizableLocalFieldsSerializer
elif django.VERSION < (1, 9):
    from .django_1_7 import CustomizableLocalFieldsSerializer
else:
    from .django_1_9 import CustomizableLocalFieldsSerializer


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
        # We convert in list because it returns a tuple in Django 1.8+
        local_m2m_fields = list(super(MultiModelInheritanceSerializer, self).get_local_m2m_fields(concrete_model))
        return local_m2m_fields + self.parent_local_m2m_fields

    def start_object(self, obj):
        # Initializing local fields we want to add current object (will be parent local fields)
        self.parent_local_fields = []
        self.parent_local_m2m_fields = []

        # Recursively getting parent fields to be added to serialization
        # We use concrete_model to avoid problems if we have to deal with proxy models
        concrete_model = obj._meta.concrete_model
        self.collect_parent_fields(concrete_model)

        super(MultiModelInheritanceSerializer, self).start_object(obj)

    def collect_parent_fields(self, model):
        # Collect parent fields that are not collected by default on non-abstract models. We call it recursively
        # to manage parents of parents, ...
        parents = model._meta.parents
        parents_to_collect = [parent for parent, parent_ptr in parents.items() if not parent._meta.abstract]

        for parent in parents_to_collect:
            self.parent_local_fields += parent._meta.local_fields
            self.parent_local_m2m_fields += parent._meta.local_many_to_many

            self.collect_parent_fields(parent._meta.concrete_model)
