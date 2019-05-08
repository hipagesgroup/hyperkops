FROM python:3.6-slim
MAINTAINER Hipages Data Science team <datascience@hipagesgroup.com.au>

ENV EXAMPLE_HOME=/usr/local/hyperkops_example

RUN mkdir -p ${EXAMPLE_HOME}
WORKDIR ${EXAMPLE_HOME}
#COPY hyperkops_example ${EXAMPLE_HOME}/hyperkops_example
#COPY setup.py ${EXAMPLE_HOME}/setup.py
COPY optimisation.py ${EXAMPLE_HOME}/optimisation.py
#RUN python ${EXAMPLE_HOME}/setup.py install
RUN pip install hyperopt==0.1.2 dill==0.2.9
ENV PYTHONUNBUFFERED: 0


ENTRYPOINT python ${EXAMPLE_HOME}/optimisation.py

