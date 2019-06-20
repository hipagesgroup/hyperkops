#!/usr/bin/env bash
## This script launches the hyperopt worker by loading
# command line arguments from the environmental variables

# Command line variables are assumed to have the prefix
# HYPEROPT_<command line arugment in uppercase>

echo "Getting Environmental Variables"

extra_arguments=""

for var in "$(env | awk -F "=" '{print $1}' | grep "HYPEROPT_ARG_.*")"; do
    # Remove prefix and make the environmental variable lowercase
    argument=$(echo "${var}" | sed -e "s/HYPEROPT_ARG_//" | sed "s/_/-/" | tr '[:upper:]' '[:lower:]')
    extra_arguments="${extra_arguments}--${argument} ${!var} "
done

echo "Starting Hyperopt worker"

# Create MongoDB Address from environmental variables
mongo_db_address="${MONGO_DB_ADDRESS}:${MONGO_DB_PORT}/${TRIALS_DB}"

echo "MongoDB Adderss ${mongo_db_address}"
## Create string of argument using the environmental variables
argument_string="hyperopt-mongo-worker --mongo ${mongo_db_address} ${extra_arguments}"

echo $argument_string

eval "${argument_string}"
