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

FROM python:2.7.15-alpine
ENV CON_PORT "8091"

EXPOSE 8091

RUN mkdir -p /etc/nginx/ssl && \
mkdir -p /var/log/conductor && \
mkdir -p /run/conductor && \
mkdir -p /run/nginx

RUN apk --update add py-setuptools && \
apk add unzip && \
apk add curl && \
apk add wget && \
apk add fcgiwrap && \
apk add bash vim && \
apk add nginx

RUN apk add py2-pip libpq python-dev
RUN pip install --upgrade pip
RUN apk add --virtual build-dependencies build-base linux-headers pcre-dev libffi-dev libxslt-dev libressl-dev
RUN pip install uwsgi

#Please leave teh following commmented out line in for test on local clusters
#RUN wget -O /tmp/has.zip "https://nexus.onap.org/service/local/repositories/autorelease-121393/content/org/onap/optf/has/optf-has-conductor/1.2.5/optf-has-conductor-1.2.5.zip" && \
RUN wget -O /tmp/has.zip "https://nexus.onap.org/service/local/artifact/maven/redirect?r=${REPO}&g=org.onap.optf.has&a=optf-has-conductor&e=zip&v=${MVN_ARTIFACT_VERSION}" && \
    unzip -q -o -B /tmp/has.zip -d /tmp/has && \
    rm -f /tmp/has.zip

#PKG-INFO file must also exists in the conductor folder (i.e. besides and inside the of_has.egg-info folder). The zip file for distro above is missing it
RUN cp /tmp/has/conductor/of_has.egg-info/PKG-INFO /tmp/has/conductor
RUN pip install -e /tmp/has/conductor

COPY app.wsgi /etc/nginx/conductor.wsgi
COPY api_paste.ini /usr/local/etc/conductor/api_paste.ini
