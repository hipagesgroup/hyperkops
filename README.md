# Hyperkops
© Hipages Group Pty Ltd 2019

This repository contains the components (collectively called Hyperkops) required to execute distributed Bayesian optimisation within
Kubernetes using the Python library [Hyperopt](https://github.com/hyperopt/hyperopt). 

The Hyperkops architecture is comprised of three main components:

* [Hyperkops Worker](https://hub.docker.com/r/hipages/hyperkops-worker) These run a hyperopt-worker, and execute each trial
* [Hyperkops Monitor](https://hub.docker.com/r/hipages/hyperkops-monitor): Identifies and updates hyperopt trials which should be logged as failed due to Pod failure or rotation
* [MongoDB](https://hub.docker.com/_/mongo): MongoDB Instance

An example helm chart can be found [here](https://github.com/hipagesgroup/chart-hyperopt).

# Hyperkops Architecture in Kubernetes

[Hyperopt](https://github.com/hyperopt/hyperopt) allows us to parallelise Bayesian optimisation jobs by distributing 
the experiments across multiple workers, with state stored and shared through a MongoDB instance. If this system is 
operated on a conventional cluster (where the underlying infrastructure is expected to be stable) is not expected to have hardware failures during any single job's lifetime
job, if a worker fails through a Python exception the hyperopt-workers emit a shutdown failure message to MongoDB, moving 
all of the worker's current jobs into a failed state, allowing the [Hyperopt](https://github.com/hyperopt/hyperopt) job to complete.

In Kubernetes the instances which execute the hyperopt-workers (Pods) can be significantly shorter lived than some
optimisation jobs and are expected to get rotated on a regular basis. If a Pod is deleted whilst executing an experiment 
the hyperopt-worker will be killed before it can emit an error signal and jobs remain in MongoDB indefinitely in a JOB_RUNNING_STATE. 
We therefore need to introduce an extra component (the Pod Monitor) to monitor our deployment, and update 
 relevant MongoDB entries for experiments we know to have been running on failed or deleted Pods.   

![ScreenShot](./img/architecture.png)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fhipagesgroup%2Fhyperkops.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fhipagesgroup%2Fhyperkops?ref=badge_shield)

## Hyperkops Monitor
The Hyperkops Monitor queries the MongoDB instance to find which Pods are labelled as currently running experiments, and 
queries the Kubernetes API to compare this list of Pods with  Pods in a RUNNING state within the cluster. Any jobs found 
to be logged as running on deleted or failed Pods are updated in MongoDB to flag them as in an `Error` state. 

### Installing Hyperkops Monitor
We recommend using the pre-built containers (links provided above). If, however, you would like to install the Python components 
this repository is not yet available in the PyPI repository so installation from github using pip is recommended.

### Starting Hyperkops Monitor

After installation with pip, the Monitor can be started from the command line. The arguments can either be provided within the
command line arguments or they can be inherited from environmental variables. 

|Command Line Argument | Environmental Variable | Description | Default Value| 
| -------------------- |:----------------------:|:-----------:|------------:|
|mongo_db_address | MONGO_DB_ADDRESS | url to MongoDB | localhost | 
|mongo_db_port | MONGO_DB_PORT| mongo db port | 27017| 
|trials_db | TRIALS_DB | Name of the MongoDB in which the trials are stored | model_db| 
|trials_collection | TRIALS_COLLECTION | Name of the Mongo Collection in which the trials are stored | jobs| 
|update_interval |UPDATE_INTERVAL | Time between queries to the MongoDB to find failed jobs | 100| 
|namespace | NAMESPACE | Namespace in which the Pods to be monitored are being deployed | | 
|label-selector | LABEL_SELECTOR | Labels which identify relevant Hyperkops worker Pods | |

Example start command:

```> hyperkops-monitor --mongo_db_address localhost --mongo_db_port 27017 --trials_db model_db --trials_collection jobs```


## Hyperkops Worker
The Hyperkops worker starts a hyperopt-worker thread, inheriting any command line arguments it requires from
suitably named environmental variables. The MongoDB address is set using the specified environmental variables, 
whilst other hyperopt-worker configurations can be set by using the naming convention: 
`HYPEROPT_<COMMAND LINE ARGUMENT NAME IN UPPER CASE>`. Examples are provided below but please refer
 to the hyperopt library itself for a comprehensive list of  [options](https://github.com/hyperopt/hyperopt/blob/master/hyperopt/mongoexp.py). 

| Environmental Variable | Description | Default Value| 
|----------------------|:-----------:|------------:|
| MONGO_DB_ADDRESS | URL to MongoDB | localhost | 
| MONGO_DB_PORT| MongoDB port | 27017| 
| TRIALS_DB | Name of the MongoDB in which the trials are stored | model_db|

Example Hyperopt Worker commands:

| Environmental Variable | Corresponding Hyperopt Command | Description |  
|----------------------|:--------------------------------:|:----------:|
| HYPEROPT_EXP_KEY| --exp-key | Identifier for this worker's jobs | 
| HYPEROPT_LAST_JOB_TIMEOUT| --last-job-timeout | Do not reserve a job after T seconds have passed | 

Example start command:

```> sh ./hyperkops/worker/kube_worker.sh```

## Fitting Master
A fitting master is any Python process which launches a [Hyperopt](https://github.com/hyperopt/hyperopt) 
optimisation job. These can either be launched from your local machine, or from a Pod within Kubenernetes. 

# Example Workload
Provided [here](./examples/optimisation.py) is an example workload which matches that seen in the [Hyperopt Documentation](http://hyperopt.github.io/hyperopt/).
A prebuilt [Docker Container](https://hub.docker.com/r/hipages/hyperkops-example) is also provided, along with an example (Kubenetes Manifest)[./examples/kube-deploy-hyperkops-infrastructure.yaml],
 a Helm chart for this infrastructure is also [available](https://github.com/hipagesgroup/chart-hyperopt).

## Starting the infrastructure
  
### Helm
Helm users can find charts for infrastructure [here](https://github.com/hipagesgroup/chart-hyperopt). This can then be launched with the command:
Note defaults for the min and max number of works, and the autoscaling criteria may need to be changed to suit your use case, and cluster size.
### Kubernetes Manifest
There is also an example Kubernetes manifest to be found [here](./examples/kube-deploy-hyperkops-infrastructure.yaml), note that this launches jobs into a namespace of `datascience`. 

```kubectl apply -f kube-deploy-hyperkops-infrastructure.yam```

## Launching jobs from your local machine
Typically external connections to pods within Kubernetes are handled by connecting their relevant service to an ingress. 
Unfortunately, this doesn't work in Kubernetes because connections to the ingress pass through an Nginx instance which expects http connections. 
To get around these limitations its possible to connect to the MongoDB instance by port forwarding the relevant service 
within Kubernetes to your local instance. In our example this is done using:

```kubectl port-forward <mongo-db pod name> 27017:27017```

Assuming you have the correct privileges to port forward within your Kubernetes environment. 
With this port forwarding in place trials can be submitting into MongoDB by addressing the relevant port on your local instance, eg:

```trials = MongoTrials(localhost:27107)```

## Launching jobs from within Kubernetes
Pods connecting within Kubernetes should connect using the relevant service endpoint and a cluster IP or domain name. 
In the chart and manifest provided this endpoint should be at:

```hyperkops-mongo.datascience.svc.cluster.local```

The example workload can be started using the Kubernetes manifest found in the [examples folder](./examples/kube-deploy-hyperkops-example.yaml), 
or by using the [helm chart](https://github.com/hipagesgroup/chart-hyperopt). 

# Future Work
* UI to allow monitoring of currently running jobs
* Create a high-avaiablilty version of MongoDb
* On-the-fly installation into the worker of required Python libraries 


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fhipagesgroup%2Fhyperkops.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fhipagesgroup%2Fhyperkops?ref=badge_large)