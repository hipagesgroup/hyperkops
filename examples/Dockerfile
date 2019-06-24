#name: hyperkops-example

FROM python:3.6-slim
MAINTAINER Hipages Data Science team <datascience@hipagesgroup.com.au>

ENV EXAMPLE_HOME=/usr/local/hyperkops_example

RUN mkdir -p ${EXAMPLE_HOME}
WORKDIR ${EXAMPLE_HOME}
COPY optimisation.py ${EXAMPLE_HOME}/optimisation.py
RUN pip install hyperopt==0.1.2 dill==0.2.9

ENTRYPOINT python ${EXAMPLE_HOME}/optimisation.py

