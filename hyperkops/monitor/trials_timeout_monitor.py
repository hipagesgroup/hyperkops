import datetime
import logging as log
import os
from time import sleep

from hyperopt import JOB_STATE_RUNNING, JOB_STATE_ERROR
from hyperopt.utils import coarse_utcnow


class MongodbTrialsTimeoutMonitor:
    """Queries the table hyperopt uses to store state and prints the results"""
    log.basicConfig(level=os.environ.get("LOGLEVEL"),
                    format='%(asctime)s %(levelname)s %(message)s')

    def __init__(self,
                 timeout_interval,
                 update_interval,
                 mongodb_connection):

        self._timeout_interval = timeout_interval
        self._update_interval = update_interval
        self._mongodb_connection = mongodb_connection

    def monitor_for_stale_jobs(self):
        """Hyperopt is designed to be deployed within a stable computing environment where the underlying instances
        are long lived. It is therefore designed around graceful failure of the worker units. If a worker fails
        through a python exception it emits a shutdown failure message to mongodb, and sets all of it current jobs to a
        failed state. In kubernetes, if a pod gets killed (which can happen when a pod
        gets deleted and moved to a different underlying instance) python won't emit this error signal,
        and jobs remain in mongo indefinitely in a JOB_RUNNING_STATE.
        This monitor helps out Hyperopt by timing out jobs which are long-lived and therefore likely associated
        with jobs which were running on pods which have been killed"""

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
            for trial in self._mongodb_connection.collection.find(
                    {'state': JOB_STATE_RUNNING, 'refresh_time': {'$lt': cur_timeout_boundary}}):
                self._log_warning_of_error(trial['_id'], trial['tid'], trial['owner'])
                # Update the state of the job to an error
                trial['state'] = JOB_STATE_ERROR
                # Upsert the job into mongodb
                self._mongodb_connection.collection.replace_one({'_id': trial['_id']}, trial, True)
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
        """
        Log an error when a job is stale
        :param obj_id: The ID of the relevant object in the mongoDB
        :param trial_id: Hyperopt Trial ID for this stale trail
        :param owner: Location of stale trial, including the pod name and pid
        :return:
        """
        warning_detail = ('obj_id : ' + str(obj_id) +
                          ":::: trial id : " + str(trial_id) +
                          ":::: Owner [pod_name, pid] : " + str(owner))

        log.warning("Forcing Job to error state due to timeout: \n" + warning_detail)


