import datetime
from unittest import TestCase

from hyperkops.monitor.running_pods_monitor import PodMonitor


class TestPodMonitor(TestCase):
    example_trial = {'state': 1, 'tid': 25, 'spec': None,
                     'result': {'status': 'new'},
                     'misc': {'tid': 25, 'cmd': ['domain_attachment', 'FMinIter_Domain'],
                              'workdir': None,
                              'idxs': {'colsample_bytree': [25],
                                       'gamma': [25], 'learning_rate': [25],
                                       'max_depth': [25], 'min_child_weight': [25],
                                       'n_estimators': [25], 'subsample': [25]},
                              'vals': {'colsample_bytree': [1.0], 'gamma': [0.7000000000000001],
                                       'learning_rate': [0.35000000000000003], 'max_depth': [8],
                                       'min_child_weight': [5.0], 'n_estimators': [83],
                                       'subsample': [0.9441004735203157]}},
                     'exp_key': None, 'owner': ['pod_1:72'],
                     'version': 0, 'book_time': datetime.datetime(2019, 3, 9, 1, 2, 45, 922000),
                     'refresh_time': datetime.datetime(2019, 3, 9, 1, 2, 45, 922000)}

    example_trial_2 = {'state': 1, 'tid': 25, 'spec': None,
                       'result': {'status': 'new'},
                       'misc': {'tid': 25, 'cmd': ['domain_attachment', 'FMinIter_Domain'],
                                'workdir': None,
                                'idxs': {'colsample_bytree': [25],
                                         'gamma': [25], 'learning_rate': [25],
                                         'max_depth': [25], 'min_child_weight': [25],
                                         'n_estimators': [25], 'subsample': [25]},
                                'vals': {'colsample_bytree': [1.0], 'gamma': [0.7000000000000001],
                                         'learning_rate': [0.35000000000000003], 'max_depth': [8],
                                         'min_child_weight': [5.0], 'n_estimators': [83],
                                         'subsample': [0.9441004735203157]}},
                       'exp_key': None, 'owner': ['pod_2:72'],
                       'version': 0, 'book_time': datetime.datetime(2019, 3, 9, 1, 2, 45, 922000),
                       'refresh_time': datetime.datetime(2019, 3, 9, 1, 2, 45, 922000)}

    def test_get_pods_running_trials(self):
        pod_monitor = PodMonitor(None, None)
        query_results = [self.example_trial, self.example_trial_2]

        running_pods = pod_monitor.get_pods_running_trials(query_results)
        self.assertEquals(running_pods, ['pod_1', 'pod_2'])

    def test_get_running_trials(self):
        owner_string = 'pod_1:72'  # owner:pid pattern

        pod_name = PodMonitor.get_pod_name_from_owner_string(owner_string)

        self.assertEquals('pod_1', pod_name)
