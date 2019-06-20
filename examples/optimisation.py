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


# The settings for the example can either be provided from command line, or loaded from
# the relevant environmental variables
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

log.info("MongoDB Address :: {}".format(mongo_api_address))
## Hyperopt settings
num_eval_steps = int(config.num_eval_steps)

# Set up the search space for hyperopt to scan over
space = hp.choice('a',
                  [('case 1', 1 + hp.lognormal('c1', 0, 1)),
                   ('case 2', hp.uniform('c2', -10, 10))])

# Extract Multiplier (used in objective function)
multiplier = float(config.multiplier)

# Assign a random exp_key so that there is no confusion between trials
exp_key = str(uuid.uuid4())

# Initialise the trials object which enables connection to the MongoDb
trials = MongoTrials(mongo_api_address, exp_key=exp_key)


# Curry function so that multiplier is included with the function
def objective_currier(multiplier):
    """
    The objective function gets curried and passed to the trials object with the data loaded
    :param multiplier: float uses to scale the objective function
    :return: objective funciton
    """

    def objective_curried(args):
        case, val = args
        log.debug(args)
        if case == 'case 1':
            return val
        else:
            return val ** multiplier

    return objective_curried


object_curried = objective_currier(multiplier)
log.info("Starting Optimisaiont")
# Run optimisation
best = fmin(fn=object_curried,
            space=space,
            algo=tpe.suggest,
            max_evals=num_eval_steps,
            trials=trials,
            verbose=1)

log.info("Finished Optimisation")
# Get the values of the best space
best_space = space_eval(space, best)

log.info("Best value in optimisation is : " + str(best_space))
