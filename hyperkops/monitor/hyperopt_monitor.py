import argparse
import logging as log
import os

from hyperkops.monitor.mongo_db_utils import MongodbConnection
from hyperkops.monitor.trials_timeout_monitor import MongodbTrialsTimeoutMonitor

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
log.basicConfig(level=LOGLEVEL)


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

    parser.add_argument("-i", "--timeout_interval",
                        dest='timeout_interval',
                        **environ_or_required("TIMEOUT_INTERVAL"),
                        metavar='float',
                        help="Maximum length of time (in seconds) for a job to run before it is considered failed")

    parser.add_argument("-u", "--update_interval",
                        dest='update_interval',
                        **environ_or_required("UPDATE_INTERVAL"),
                        metavar='float',
                        help="Time between queries to the MongoDb to find failed jobs")

    args = parser.parse_args()

    return HyperoptMonitor(args)


class HyperoptMonitor:
    """Instantiation and starting of the hyperopt monitoring tool"""

    def __init__(self, config):

        self.args = args
        log.info("Starting Monitor")
        self.start_monitoring()

    def start_monitoring(self):
        """
        Initalisation of long running job to monitor for stale hyperopt jobs
        :return: None
        """
        mongodb_connection = MongodbConnection(self.args.mongo_db_address,
                                               int(self.args.mongo_db_port),
                                               self.args.trials_db,
                                               self.args.trials_collection)

        hyperopt_timeout_monitor = MongodbTrialsTimeoutMonitor(float(self.args.timeout_interval),
                                                               float(self.args.update_interval),
                                                               mongodb_connection)

        hyperopt_timeout_monitor.monitor_for_stale_jobs()
