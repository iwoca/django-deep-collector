from copy import copy
import json
from django.test import TestCase

from .factories import ChildModelFactory
from deep_collector.compat.serializers import MultiModelInheritanceSerializer


class TestMultiModelInheritanceSerializer(TestCase):

    def test_that_parent_model_fields_are_in_serializated_object_if_parent_is_not_abstract(self):
        child_model = ChildModelFactory.create()

        serializer = MultiModelInheritanceSerializer()
        json_objects = serializer.serialize([child_model])

        child_model_dict = json.loads(json_objects)[0]
        serialized_fields = child_model_dict['fields'].keys()
        self.assertIn('child_field', serialized_fields)
        self.assertIn('o2o', serialized_fields)
        self.assertIn('fkey', serialized_fields)

    def test_that_we_dont_alter_model_class_meta_after_serialization(self):
        child_model = ChildModelFactory.create()
        local_fields_before = copy(child_model._meta.concrete_model._meta.local_fields)
        local_m2m_fields_before = copy(child_model._meta.concrete_model._meta.local_many_to_many)

        serializer = MultiModelInheritanceSerializer()
        serializer.serialize([child_model])

        local_fields_after = copy(child_model._meta.concrete_model._meta.local_fields)
        local_m2m_fields_after = copy(child_model._meta.concrete_model._meta.local_many_to_many)

        self.assertEqual(local_fields_before, local_fields_after)
        self.assertEqual(local_m2m_fields_before, local_m2m_fields_after)
