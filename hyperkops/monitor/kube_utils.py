import logging as log

from kubernetes import client, config


class KubeUtil:
    def __init__(self, namespace):
        log.info("Initialising Kuberenetes Connection")
        config.load_incluster_config()
        self.core_api = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()
        self.extensions_api = client.ExtensionsV1beta1Api()
        self.namespace = namespace

    def list_pods(self):
        """
        list of pods in the namespace
        :return: dict object returned from the api
        """
        ret = self.core_api.list_namespaced_pod(namespace=self.namespace, watch=False)
        return ret

    def get_status_of_all_pods(self, selector):
        """
        Get the pods and their phase status
        :param selector: the label selector string in the key=value,key2=value2 format
        :return: a list of dicts eg. [{'pod':'foo', 'phase':'succeeded'}]
        """
        print("Sensing pod statuses with selector {}".format(selector))
        pod_list = self.core_api.list_namespaced_pod(namespace=self.namespace, watch=False, label_selector=selector)
        # Type is V1PodList https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodList.md
        # print("api response {}".format(pod_list))
        statuses = []
        for i in pod_list.items:
            # i is of type V1Pod https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Pod.md
            statuses.append({'pod': i.metadata.name, 'phase': i.status.phase})
        return statuses

    def get_running_pods(self, selector):
        """
        Get a list of the names of running pods
        :param selector: the label selector string in the key=value,key2=value2 format
        :return: a list of names of running pods
        """
        pod_status = self.get_status_of_all_pods(selector)

        return [pod_info['pod'] for pod_info in pod_status if pod_info['phase'] == 'running']
