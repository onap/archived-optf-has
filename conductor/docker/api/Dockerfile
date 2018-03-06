FROM python:2.7
ENV CON_ADDR "127.0.0.1"
ENV CON_PORT "8091"

EXPOSE 8091

RUN apt-get update
RUN apt-get --assume-yes install python-setuptools
RUN apt-get install -y unzip
RUN apt-get install -y curl
RUN apt-get install -y wget

# TODO (Ikram): We are having issues with running pip install -e . from the 'zipped' version downloaded from Nexus.
# This is why we are using the git clone instead. This is only temporary, We need this merged as a test-bench first
# in order to test other parts of the docker upload chain process in ONAP.
# RUN rm -rf ./conductor
# RUN rm -rf ./optf-has-conductor.zip
# RUN wget -q -O optf-has-conductor.zip 'https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.optf.has&a=optf-has-conductor&v=LATEST&e=zip' && \
#     unzip optf-has-conductor && \
#     rm -rf optf-has-conductor.zip && \
#     pip install -r conductor/requirements.txt

#WORKDIR ./conductor/conductor

RUN rm -rf ./has
RUN git clone https://gerrit.onap.org/r/optf/has
WORKDIR ./has/conductor/conductor
RUN virtualenv ./venv && . ./venv/bin/activate
RUN pip install -e .
CMD ["sh","-c", "python /usr/local/bin/conductor-api --port=8091 -- --config-file=conductor.conf"]

