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
ENV CON_PORT "8091"

EXPOSE 8091
RUN apt-get update && apt-get --assume-yes install python-setuptools && \
apt-get install -y unzip && \
apt-get install -y curl && \
apt-get install -y wget && \
apt-get install -y nginx && \
apt-get install -y fcgiwrap

RUN mkdir -p /etc/nginx/ssl && \
mkdir -p /var/log/conductor && \
mkdir -p /run/conductor

RUN apt-get install -y python-pip libpq-dev python-dev
RUN pip install --upgrade pip
RUN pip install uwsgi

RUN wget -O /tmp/has.zip "https://nexus.onap.org/service/local/artifact/maven/redirect?r=${REPO}&g=org.onap.optf.has&a=optf-has-conductor&e=zip&v=${MVN_ARTIFACT_VERSION}" && \
    unzip -q -o -B /tmp/has.zip -d /tmp/has && \
    rm -f /tmp/has.zip

RUN cp /tmp/has/conductor/of_has.egg-info/PKG-INFO /tmp/has/conductor
RUN pip install -e /tmp/has/conductor
COPY app.wsgi /etc/nginx/conductor.wsgi
COPY api_paste.ini /usr/local/bin/api_paste.ini
COPY api_paste.ini /usr/local/etc/conductor/api_paste.ini
COPY conductor /etc/nginx/sites-enabled
COPY conductor /etc/nginx/sites-available
