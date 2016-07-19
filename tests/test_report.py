from django.test import TestCase

from deep_collector.core import RelatedObjectsCollector

from .factories import BaseModelFactory, ForeignKeyToBaseModelFactory


class TestLogReportGeneration(TestCase):
    def test_report_with_no_debug_mode(self):
        obj = BaseModelFactory.create()

        collector = RelatedObjectsCollector()
        collector.collect(obj)
        report = collector.get_report()

        self.assertDictEqual(report, {
            'excluded_fields': [],
            'log': 'Set DEBUG to True to get collector internal logs'
        })

    def test_report_with_debug_mode(self):
        self.maxDiff = None
        obj = BaseModelFactory.create()

        collector = RelatedObjectsCollector()
        collector.DEBUG = True
        collector.collect(obj)
        report = collector.get_report()

        self.assertEqual(report['excluded_fields'], [])
        # For now, just checking that the log report is not empty.
        # Some work has to be done to test it more.
        self.assertNotEqual(report['log'], [])


class TestExcludedFieldLogReportGeneration(TestCase):

    def test_excluded_field_report(self):
        obj = BaseModelFactory.create()
        ForeignKeyToBaseModelFactory.create_batch(fkeyto=obj, size=3)

        collector = RelatedObjectsCollector()
        collector.MAXIMUM_RELATED_INSTANCES = 3
        collector.collect(obj)

        self.assertEquals(len(collector.get_report()['excluded_fields']), 0)

        # If we have more related objects than expected, we are not collecting them, to avoid a too big collection
        collector.MAXIMUM_RELATED_INSTANCES = 2
        collector.collect(obj)

        self.assertEquals(len(collector.get_report()['excluded_fields']), 1)
