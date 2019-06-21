#name: hyperkops-worker
FROM python:3.6-slim

ENV WORKER_HOME=/usr/local/hyperopt_worker

RUN mkdir -p ${WORKER_HOME}

RUN pip install hyperopt==0.1.2 dill==0.2.9

COPY kube_worker.sh ${WORKER_HOME}/kube_worker.sh

ENTRYPOINT ${WORKER_HOME}/kube_worker.sh
