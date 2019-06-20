#!/usr/bin/env bash
## This script launches the hyperopt worker by loading
# command line arguments from the environmental variables

# Command line variables are assumed to have the prefix
# HYPEROPT_<command line arugment in uppercase>

echo "Getting Environmental Variables"

mongo_db_address=${MONGO_DB_ADDRESS:-localhost}
mongo_db_port=${MONGO_DB_PORT:-27017}
trials_db=${TRIALS_DB:-model_db}


# Create MongoDB Address from environmental variables
mongo_db_full_qualified_address="${mongo_db_address}:${mongo_db_port}/${TRIALS_DB}"

echo "MongoDB Address ${mongo_db_full_qualified_address}"
## Create a string of arguments using the environmental variables
argument_string="hyperopt-mongo-worker --mongo ${mongo_db_full_qualified_address} "

for var in "${!HYPEROPT_@}"; do
    # Remove prefix and make the environmental variable lowercase
    argument=$(echo "${var}" | sed -e "s/^HYPEROPT_//" | sed "s/_/-/" | tr '[:upper:]' '[:lower:]')
    argument_string="${argument_string}--${argument} ${!var} "
done

echo "Starting Hyperopt worker"

eval "${argument_string}"
