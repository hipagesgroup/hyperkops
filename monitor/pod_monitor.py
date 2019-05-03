import datetime
import os
import logging as log
from time import sleep
from hyperopt import JOB_STATE_RUNNING, JOB_STATE_ERROR
from hyperopt.utils import coarse_utcnow
from monitor.mongo_db_utils import MongodbConnection


class MongodbTrialsTimeoutMonitor(MongodbConnection):
    """Queries the table hyperopt uses to store state and prints the results"""
    log.basicConfig(level=os.environ.get("LOGLEVEL"), format='%(asctime)s %(levelname)s %(message)s')

    def __init__(self,
                 mongo_db_address=None,
                 mongo_db_port=None,
                 timeout_interval=None,
                 update_interval=None):
        self._timeout_interval = timeout_interval if timeout_interval is not None else int(
            os.environ['TRIALS_TIMEOUT_INTERVAL'])
        self._db_name = "model_db"
        self._collection_name = "jobs"
        self._update_interval = update_interval if update_interval is not None else int(
            os.environ['UPDATE_INTERVAL'])

        super().__init__(mongo_db_address, mongo_db_port)

    def _init_jobs_collection(self):
        """Initialise connection to jobs collection
        :return None
        """
        self.init_connection_to_collection(self._db_name, self._collection_name)

    def error_stale_jobs(self):
        """Hyperopt is designed to be deployed within a stable computing environment where the underlying instances
        are long lived. It is therefore designed around graceful failure of the worker units. If a worker fails
        through a python exception it emits a shutdown failure message to mongodb, and sets all of it current jobs to a
        failed state. In kubernetes, if a pod gets killed (which can happen when a pod
        gets deleted and moved to a different underlying instance) python won't emit this error signal,
        and jobs remain in mongo indefinitely in a JOB_RUNNING_STATE.
        This monitor helps out Hyperopt by timing out jobs which are long-lived and therefore likely associated
        with jobs which were running on pods which have been killed"""

        self._init_jobs_collection()
        while True:
            log.info("Checking for stale jobs")
            cur_timeout_boundary = self._get_current_timeout_boundary(self._timeout_interval)
            counter = 0

            # In trial DB refresh time is the last time a document was updated by the worker
            # Updates typically happen when a job is taken by a worker, and the job state is set to JOB_STATE_RUNNING
            # JOB_STATE_FINISHED, or JOB_STATE_NEW. This refresh time can therefore be used to monitor
            # how long a job has been running on a worker, and used to timeout any log running jobs

            # Query the Mongo DB for jobs which extend past teh timeout bounday, and iterate through the doucments
            # upserting them to an error state
            for trial in self._collection.find(
                    {'state': JOB_STATE_RUNNING, 'refresh_time': {'$lt': cur_timeout_boundary}}):
                self._log_warning_of_error(trial['_id'], trial['tid'], trial['owner'])
                # Update the state of the job to an error
                trial['state'] = JOB_STATE_ERROR
                # Upsert the job into mongodb
                self._collection.replace_one({'_id': trial['_id']}, trial, True)
                counter = counter + 1
            log.info("Stale job check complete")
            log.info("Number of stale jobs found :: " + str(counter))
            sleep(self._update_interval)

    @staticmethod
    def _get_current_timeout_boundary(timeout_interval):
        """
        Use Hyperopts own UTC time format to get current time and then subtract the timeout window
        :return: datetime.datetime(<Ageout time>)
        """
        return coarse_utcnow() - datetime.timedelta(minutes=timeout_interval)

    @staticmethod
    def _log_warning_of_error(obj_id, trial_id, owner):
        warning_detail = ('obj_id : ' + str(obj_id) +
                          ":::: trial id : " + str(trial_id) +
                          ":::: Owner [pod_name, pid] : " + str(owner))

        log.warning("Forcing Job to error state due to timeout: \n" + warning_detail)




if __name__ == "__main__":
    print("Starting logging")
    log.info("Starting logging")
    mongo_jobs_logger = MongodbTrialsTimeoutMonitor()
    mongo_jobs_logger.error_stale_jobs()
