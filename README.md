# Hyperkops 
© Hipages Group Pty Ltd 2019

Monitor to supervise hyperopt deployment in K8s
Hyperopt is designed to be deployed within a stable computing environment where the underlying instances
are long lived, and the state of the asynchronous calcuation is held in MongoDb.

Hyperopt is designed around graceful failure of the worker units. If a worker fails
through a python exception it emits a shutdown failure message to mongodb, and sets all of it current jobs to a
failed state. In kubernetes, if a pod gets killed (which can happen when a pod
gets deleted or rotated to a different underlying instance) python won't emit this error signal,
and jobs remain in MongoDB indefinitely in a JOB_RUNNING_STATE. This monitor helps out Hyperopt by identifying jobs which 
fit this category of killed jobs, and updates the relevant MongoDB record, allowing the optimisation to finish.  

This repository produces the docker image that can be used in the hyperopt helm chart as the job monitor component.

# Architecture in kubernetes

* Worker: Hyperopt worker pod
* MongoDB: MongoDB Instance
* Stale Job Timer


# Stru


Also, publishes images to docker hub.
