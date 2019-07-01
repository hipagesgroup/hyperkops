#name: hyperkops-monitor

FROM python:3.6-slim AS base_container
MAINTAINER Hipages Data Science team <datascience@hipagesgroup.com.au>

ENV HYPERKOPS_HOME=/usr/local/hyperkops
RUN mkdir -p ${HYPERKOPS_HOME}
WORKDIR ${HYPERKOPS_HOME}
COPY hyperkops ${HYPERKOPS_HOME}/hyperkops
COPY setup.py setup.py
# adding testing layer
FROM base_container AS test_container
COPY tests ${HYPERKOPS_HOME}/tests
COPY requirements.txt ${HYPERKOPS_HOME}/requirements.txt
RUN  pip install -r ${HYPERKOPS_HOME}/requirements.txt
RUN py.test -v --cov=.  --cov-config .coveragerc

FROM base_container AS production_container
RUN pip install --upgrade pip && \
    python ${HYPERKOPS_HOME}/setup.py install
ENTRYPOINT hyperkops-monitor
