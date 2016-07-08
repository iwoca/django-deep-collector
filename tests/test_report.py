from django.test import TestCase

from deep_collector.core import RelatedObjectsCollector

from .factories import BaseModelFactory


class TestLogReportGeneration(TestCase):
    def test_report_with_no_debug_mode(self):
        obj = BaseModelFactory.create()

        collector = RelatedObjectsCollector()
        collector.collect(obj)
        report = collector.get_report()

        self.assertDictEqual(report, {
            'excluded_fields': [],
            'log': 'Set DEBUG to True if you what collector internal logs'
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
