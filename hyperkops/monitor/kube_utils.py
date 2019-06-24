import logging as log

from kubernetes import client, config


class KubeUtil:
    def __init__(self, namespace):
        log.info("Initialising Kuberenetes Connection")
        config.load_incluster_config()
        self.core_api = client.CoreV1Api()
        self.namespace = namespace

    def get_status_of_all_pods(self, label_selector):
        """
        Get the pods and their phase status
        :param label_selector: the label selector string in the 'label=label1' or label is in (label1, label2)
        :return: a list of dicts eg. [{'pod':'foo', 'phase':'succeeded'}]
        """
        log.info("Sensing pod statuses with selector {}".format(label_selector))

        if label_selector is None:
            pod_list = self.core_api.list_namespaced_pod(namespace=self.namespace)
        else:
            pod_list = self.core_api.list_namespaced_pod(namespace=self.namespace,
                                                         label_selector=label_selector)
        statuses = []
        for i in pod_list.items:
            # i is of type V1Pod https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Pod.md
            statuses.append({'pod': i.metadata.name, 'phase': i.status.phase})

        log.debug(statuses)

        return statuses

    def get_running_pods(self, selector):
        """
        Get a list of the names of running pods
        :param selector: the label selector string in the key=value,key2=value2 format
        :return: a list of names of running pods
        """
        pod_status = self.get_status_of_all_pods(selector)

        return [pod_info['pod'] for pod_info in pod_status if pod_info['phase'] == 'running']
