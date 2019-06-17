import logging as log
from collections import Counter

from hyperopt import JOB_STATE_RUNNING, JOB_STATE_ERROR


class PodMonitor:

    def __init__(self,
                 kube_connector,
                 mongodb_connection,
                 selector):

        self.kube_api_connector = kube_connector
        self.mongodb_connection = mongodb_connection
        self.selector = selector

    def remove_dead_trials(self):
        """
        Queries the Kubernetes API to find a list of running pods, and upserts trials
        in MongoDB as failed
        :return: None
        """
        running_pods = self.kube_api_connector.get_running_pods(self.selector)

        query_results = self.get_running_trials()
        pods_running_trials = self.get_pods_running_trials(query_results)
        deleted_pods = set(pods_running_trials) - set(running_pods)

        self.upsert_jobs_on_deleted_pods(deleted_pods, query_results)

    def upsert_jobs_on_deleted_pods(self, deleted_pods, query_results):
        """
        Upserts records where the pod is no-longer running
        :param deleted_pods: List of string names of the deleted pods
        :param query_results: list of dictionaries of the currently running trials
        :return: None
        """
        counter = 0
        for trial in query_results:
            if self.get_pod_name_from_owner_string(trial['owner'][0]) in list(deleted_pods):
                trial['state'] = JOB_STATE_ERROR
                log.warning("Trial deleted from MongoDB owner = " + str(trial['owner'][0]))
                # Upsert the job into mongodb
                self.mongodb_connection.collection.replace_one({'_id': trial['_id']}, trial, True)
                counter += 1

        log.info("Number of stale jobs detected : " + str(counter))
    def get_pods_running_trials(self, query_results):
        """
        Uses the results to find the unique names of pods running trials
        :param query_results: List of dictionaries, each dictionary is a running trial
        :return: list of string pod names
        """

        log.debug("Running Trials ::")

        owner_counters = Counter()
        for trial in query_results:
            owner_counters[self.get_pod_name_from_owner_string(trial['owner'][0])] += 1
            log.debug(trial)
        pods_running_trials = list(owner_counters.keys())

        return pods_running_trials

    @staticmethod
    def get_pod_name_from_owner_string(owner_string):
        """
        Splits the owner string to find the pod name
        :param owner_string: string associated with the trial owner, string is structured as pod_name:pid
        :return: pod names a string
        """
        return str.split(owner_string, ":")[0]

    def get_running_trials(self):
        """
        Query the MongoDB to find running trials
        :return: list of dictrionaries for the running trials
        """
        return [trial for trial in self.mongodb_connection.collection.find({'state': JOB_STATE_RUNNING})]
