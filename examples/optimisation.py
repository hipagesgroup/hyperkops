# This script executes an example workload on the kubenetes infrastructure.

import argparse
import logging as log
import os
import uuid

from hyperopt import hp, fmin, tpe, space_eval
from hyperopt.mongoexp import MongoTrials


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

parser.add_argument("-e", "--num_eval_steps",
                    dest='num_eval_steps',
                    **environ_or_required("NUM_EVAL_STEPS"),
                    metavar='int',
                    help="Name of hyperopt evaluation steps")

parser.add_argument("-m", "--multiplier",
                    dest='multiplier',
                    **environ_or_required("MULTIPLIER"),
                    metavar='float',
                    help="Multiplier used in example optimisation")

config = parser.parse_args()

# Set up mongo addresses
mongo_db_address = config.mongo_db_address
mongo_db_port = int(config.mongo_db_port)
mongo_protocol = 'mongo'

trials_db = config.trials_db
trials_collection = config.trials_collection

mongo_api_address = "%s://%s:%s/%s/%s" % \
                    (mongo_protocol,
                     mongo_db_address,
                     mongo_db_port,
                     trials_db,
                     trials_collection)

num_eval_steps = int(config.num_eval_steps)
multiplier = float(config.multiplier)

space = hp.choice('a',
                  [('case 1', 1 + hp.lognormal('c1', 0, 1)),
                   ('case 2', hp.uniform('c2', -10, 10))])

"Initalise the trials object which stores the current state of the optimisation"
exp_key = str(uuid.uuid4())
trials = MongoTrials(mongo_api_address, exp_key=exp_key)


def objective_currier(multiplier):
    """
    The objective function gets curried and passed to the trials object with the data loaded
    :return: curried objective function
    """

    def objective_curried(args):
        case, val = args
        if case == 'case 1':
            return val
        else:
            return val ** multiplier

    return objective_curried


object_curried = objective_currier(multiplier)

best = fmin(fn=object_curried,
            space=space,
            algo=tpe.suggest,
            max_evals=num_eval_steps,
            trials=trials,
            verbose=1)

best_space = space_eval(space, best)

log.info("Best value in optimsation is : " + str(best_space))
