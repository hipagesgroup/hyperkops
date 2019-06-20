import uuid
from unittest import TestCase

from hyperkops.monitor.hyperopt_monitor import HyperoptMonitor


class TestHyperoptMonitor(TestCase):

    def test_parsing_single_labels(self):
        single_label = str(uuid.uuid4().hex)
        returned_string = HyperoptMonitor.parse_labels(single_label)
        assert returned_string == 'label=' + single_label

    def test_parsing_multiple_labels(self):
        multi_label = ','.join([str(uuid.uuid4().hex), str(uuid.uuid4().hex)])
        returned_string = HyperoptMonitor.parse_labels(multi_label)
        assert returned_string == 'label in (' + multi_label + ')'
