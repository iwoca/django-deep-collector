from copy import copy
import json
from django.test import TestCase

from deep_collector.factories import (BaseModelFactory, ManyToManyToBaseModelFactory,
                                        ForeignKeyToBaseModelFactory, ClassLevel3Factory,
                                        ManyToManyToBaseModelWithRelatedNameFactory, ChildModelFactory)
from deep_collector.serializers import MultiModelInheritanceSerializer
from deep_collector.utils import RelatedObjectsCollector


class TestDirectRelations(TestCase):

    def test_get_foreign_key_object(self):
        obj = BaseModelFactory.create()

        collector = RelatedObjectsCollector()
        collector.collect(obj)
        self.assertIn(obj.fkey, collector.get_collected_objects())

    def test_get_one_to_one_object(self):
        obj = BaseModelFactory.create()

        collector = RelatedObjectsCollector()
        collector.collect(obj)
        self.assertIn(obj.o2o, collector.get_collected_objects())

    def test_get_many_to_many_object(self):
        obj = BaseModelFactory.create()
        m2m_model = ManyToManyToBaseModelFactory.create(base_models=[obj])

        collector = RelatedObjectsCollector()
        collector.collect(m2m_model)
        self.assertIn(obj, collector.get_collected_objects())


class TestReverseRelations(TestCase):

    def test_get_reverse_foreign_key_object(self):
        fkey_model = ForeignKeyToBaseModelFactory.create()

        collector = RelatedObjectsCollector()
        collector.collect(fkey_model.fkeyto)
        self.assertIn(fkey_model, collector.get_collected_objects())

    def test_get_reverse_many_to_many_object(self):
        obj = BaseModelFactory.create()
        m2m_model = ManyToManyToBaseModelFactory.create(base_models=[obj])

        collector = RelatedObjectsCollector()
        collector.collect(obj)
        self.assertIn(m2m_model, collector.get_collected_objects())


class TestNestedObjects(TestCase):

    def test_recursive_foreign_keys(self):
        level3 = ClassLevel3Factory.create()
        level2 = level3.fkey
        level1 = level2.fkey

        collector = RelatedObjectsCollector()

        # Double reverse field collection
        collector.collect(level1)
        collected_objs = collector.get_collected_objects()
        self.assertIn(level1, collected_objs)
        self.assertIn(level2, collected_objs)
        self.assertIn(level3, collected_objs)

        # Middle class collection (1 direct field and 1 reverse field)
        collector.collect(level2)
        collected_objs = collector.get_collected_objects()
        self.assertIn(level1, collected_objs)
        self.assertIn(level2, collected_objs)
        self.assertIn(level3, collected_objs)

        # Double direct field collection
        collector.collect(level3)
        collected_objs = collector.get_collected_objects()
        self.assertIn(level1, collected_objs)
        self.assertIn(level2, collected_objs)
        self.assertIn(level3, collected_objs)


class TestCollectorParameters(TestCase):

    def test_model_is_excluded_when_defined_in_models_exclude_list(self):
        obj = BaseModelFactory.create()

        collector = RelatedObjectsCollector()
        collector.EXCLUDE_MODELS = ['nested_collector.o2odummymodel']
        collector.collect(obj)

        self.assertNotIn(obj.o2o, collector.get_collected_objects())

    def test_direct_field_is_excluded_when_defined_in_direct_field_exclude_list(self):
        obj = BaseModelFactory.create()

        collector = RelatedObjectsCollector()
        collector.EXCLUDE_DIRECT_FIELDS = {
            'nested_collector.basemodel': ['fkey']
        }
        collector.collect(obj)

        self.assertNotIn(obj.fkey, collector.get_collected_objects())

    def test_related_field_is_excluded_when_defined_in_related_field_exclude_list(self):
        obj = BaseModelFactory.create()
        m2m_model = ManyToManyToBaseModelFactory.create(base_models=[obj])

        collector = RelatedObjectsCollector()
        collector.EXCLUDE_RELATED_FIELDS = {
            'nested_collector.basemodel': ['manytomanytobasemodel_set']
        }
        collector.collect(obj)

        self.assertNotIn(m2m_model, collector.get_collected_objects())

    def test_related_field__with_related_name_is_excluded_when_defined_in_related_field_exclude_list(self):
        obj = BaseModelFactory.create()
        m2m_model = ManyToManyToBaseModelWithRelatedNameFactory.create(base_models=[obj])

        collector = RelatedObjectsCollector()
        collector.EXCLUDE_RELATED_FIELDS = {
            'nested_collector.basemodel': ['custom_related_m2m_name']
        }
        collector.collect(obj)

        self.assertNotIn(m2m_model, collector.get_collected_objects())


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
