#name: hyperkops-monitor
FROM python:3.6-slim
MAINTAINER Hipages Data Science team <datascience@hipagesgroup.com.au>


ENV HYPERKOPS_HOME=/usr/local/hyperkops
RUN mkdir -p ${HYPERKOPS_HOME}
WORKDIR ${HYPERKOPS_HOME}
COPY hyperkops ${HYPERKOPS_HOME}/hyperkops
COPY setup.py setup.py

RUN pip install --upgrade pip && \
    python ${HYPERKOPS_HOME}/setup.py install

ENTRYPOINT hyperkops-monitor