FROM python:3.6-slim AS base
MAINTAINER Hipages Data Science team <datascience@hipagesgroup.com.au>
ENV HYPERKOPS_HOME=/usr/local/hyperkops

RUN mkdir -p ${HYPERKOPS_HOME}
WORKDIR ${HYPERKOPS_HOME}

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r ${HYPERKOPS_HOME}/requirements.txt

FROM base AS test

# Copy in testing

COPY tests/requirements.txt ${HYPERKOPS_HOME}/tests/requirements.txt
RUN  pip install -r ${HYPERKOPS_HOME}/tests/requirements.txt
COPY monitor monitor
COPY launcher launcher
COPY tests tests
RUN py.test -v --cov=.  --cov-config .coveragerc

FROM base AS run

COPY monitor monitor
COPY launcher launcher
COPY run.sh run.sh

ENTRYPOINT run.sh

