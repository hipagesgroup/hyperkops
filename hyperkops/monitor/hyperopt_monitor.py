import argparse
import logging as log
import os
from time import sleep

from hyperkops.monitor.kube_utils import KubeUtil
from hyperkops.monitor.mongo_db_utils import MongodbConnection
from hyperkops.monitor.pods_monitor import PodMonitor

log.basicConfig(level=os.environ.get('LOGLEVEL', 'WARNING').upper())


def main_monitor():
    """Main entry point from command line to initialise the hyperopt stale job monitor"""

    def environ_or_required(key):
        if os.environ.get(key):
            return {'default': os.environ.get(key)}
        else:
            log.error("Missing " + str(key.lower())
                      + " configuration. Please use command line argument or environment variable " + key)
            return {'required': True}

    parser = argparse.ArgumentParser()
    parser.add_argument("-d",
                        "--mongo_db_address",
                        dest='mongo_db_address',
                        **environ_or_required("MONGO_DB_ADDRESS"),
                        metavar='str',
                        help="url to monogo db")

    parser.add_argument("-p", "--mongo_db_port",
                        dest='mongo_db_port',
                        **environ_or_required("MONGO_DB_PORT"),
                        metavar='str',
                        help="mongo db port")

    parser.add_argument("-t", "--trials_db",
                        dest='trials_db',
                        **environ_or_required("TRIALS_DB"),
                        metavar='str',
                        help="Name of the Mongo Database in which the trials are stored")

    parser.add_argument("-c", "--trials_collection",
                        dest='trials_collection',
                        **environ_or_required("TRIALS_COLLECTION"),
                        metavar='str',
                        help="Name of the Mongo Collection in which the trials are stored")

    parser.add_argument("-u", "--update_interval",
                        dest='update_interval',
                        **environ_or_required("UPDATE_INTERVAL"),
                        metavar='float',
                        help="Time between queries to the MongoDb to find failed jobs")

    parser.add_argument("-n", "--namespace",
                        dest='namespace',
                        **environ_or_required("NAMESPACE"),
                        metavar='float',
                        help="Namespace in which the pods are deployed")

    parser.add_argument("-s", "--label-selector",
                        dest='label-selector',
                        **environ_or_required("LABEL_SELECTOR"),
                        metavar='float',
                        help="Pod selector for the workers, format of key=value or key in (value1, value2)")

    args = parser.parse_args()

    return HyperoptMonitor(args)


class HyperoptMonitor:
    """Instantiation and starting of the hyperopt monitoring tool"""

    def __init__(self, config):
        self.config = config
        log.info("Starting Monitor")
        self.update_interval = float(config.update_interval)

        self.start_monitoring()

    def start_monitoring(self):
        """
        Initalisation of long running job to monitor for stale hyperopt jobs
        :return: None
        """
        mongodb_connection = MongodbConnection(self.config.mongo_db_address,
                                               int(self.config.mongo_db_port),
                                               self.config.trials_db,
                                               self.config.trials_collection)

        kube_api_connector = KubeUtil(namespace=self.config.namespace)

        pod_monitor = PodMonitor(kube_api_connector,
                                 mongodb_connection,
                                 self.config.selector)

        while True:
            pod_monitor.remove_dead_trials()

            sleep(self.update_interval)


