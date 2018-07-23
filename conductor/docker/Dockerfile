# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------

FROM python:2.7

ARG MVN_ARTIFACT_VERSION
ARG REPO
ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY
ENV CON_ADDR "127.0.0.1"
ENV CON_PORT "8091"

EXPOSE ${CON_PORT}

RUN apt-get update && apt-get --assume-yes install python-setuptools && \
apt-get install -y unzip curl wget git vim

# HAS
WORKDIR /opt/has
RUN wget -O /opt/has.zip "https://nexus.onap.org/service/local/artifact/maven/redirect?r=${REPO}&g=org.onap.optf.has&a=optf-has-conductor&e=zip&v=${MVN_ARTIFACT_VERSION}" && \
    unzip -q -o -B /opt/has.zip -d /opt/has && \
    rm -f /opt/has.zip
RUN mkdir -p /var/log/onap/optf/has/

RUN cd /opt/has/conductor/ && git init && pip install -e .
COPY api_paste.ini /usr/local/bin/api_paste.ini
