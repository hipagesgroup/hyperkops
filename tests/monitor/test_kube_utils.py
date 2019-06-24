from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from kubernetes.client import V1PodList, V1Pod, V1ObjectMeta, V1PodStatus

from hyperkops.monitor.kube_utils import KubeUtil


class TestKubeUtil(TestCase):

    @patch('hyperkops.monitor.kube_utils.KubeUtil')
    def test_get_pod_statuses_single(self, kube):
        # Mocking kube api - https://github.com/kubernetes-client/python/blob/9b438eed5a4fdab4377515b5a0c62d695dffc354/kubernetes/docs/V1PodList.md
        kube.core_api.list_namespaced_pod = MagicMock(
            return_value=V1PodList(
                api_version='v1',
                items=[
                    V1Pod(
                        api_version='v1',
                        kind='Pod',
                        metadata=V1ObjectMeta(name="pod_1"),
                        spec=None,
                        status=V1PodStatus(phase='failed')
                    ),
                    V1Pod(
                        api_version='v1',
                        kind='Pod',
                        metadata=V1ObjectMeta(name="pod_2"),
                        spec=None,
                        status=V1PodStatus(phase='pending')
                    ),
                    V1Pod(
                        api_version='v1',
                        kind='Pod',
                        metadata=V1ObjectMeta(name="pod_3"),
                        spec=None,
                        status=V1PodStatus(phase='running')
                    )
                ]
            )
        )

        actual = KubeUtil.get_status_of_all_pods(kube, label_selector="label=bar")
        self.assertEquals(actual, [{'pod': 'pod_1', 'phase': 'failed'},
                                   {'pod': 'pod_2', 'phase': 'pending'},
                                   {'pod': 'pod_3', 'phase': 'running'}])

    @patch('hyperkops.monitor.kube_utils.KubeUtil')
    def test_get_only_running_pods(self, kube):
        # Mocking kube api - https://github.com/kubernetes-client/python/blob/9b438eed5a4fdab4377515b5a0c62d695dffc354/kubernetes/docs/V1PodList.md
        kube.get_status_of_all_pods = MagicMock(
            return_value=[{'pod': 'pod_1', 'phase': 'failed'},
                          {'pod': 'pod_2', 'phase': 'pending'},
                          {'pod': 'pod_3', 'phase': 'running'}]
        )

        actual = KubeUtil.get_running_pods(kube, selector="foo=bar")
        self.assertEquals(actual, ['pod_3'])
        # self.assertEquals(1,2)
