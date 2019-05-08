#!/usr/bin/env bash
## This script launches the hyperopt worker by loading
# command line arguments from the environmental variables

# Command line variables are assumed to have the prefix
# HYPEROPT_<command line arugment in uppercase>

echo "Getting Environmental Variables"

# Create MongoDB Address from environmental variables
mongo_db_address="${MONGO_DB_ADDRESS}:${MONGO_DB_PORT}/${TRIALS_DB}"

echo "MongoDB Adderss ${mongo_db_address}"
## Create string of argument using the environmental variables
argument_string="hyperopt-mongo-worker --mongo ${mongo_db_address} "

for var in "${!HYPEROPT_@}"; do
    # Remove prefix and make the environmental variable lowercase
    argument=$(echo "${var}" | sed -e "s/^HYPEROPT_//" | sed "s/_/-/" | tr '[:upper:]' '[:lower:]')
    argument_string="${argument_string}--${argument} ${!var} "
done
echo "Starting Hyperopt worker"

eval "${argument_string}"