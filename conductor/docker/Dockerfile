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

FROM python:3.8.0-alpine


ARG MVN_ARTIFACT_VERSION
ARG REPO
ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY
ENV CON_ADDR "127.0.0.1"
ENV CON_PORT "8091"
EXPOSE ${CON_PORT}

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

RUN wget -O /opt/has.zip "https://nexus.onap.org/service/local/artifact/maven/redirect?r=${REPO}&g=org.onap.optf.has&a=optf-has-conductor&e=zip&v=${MVN_ARTIFACT_VERSION}" && \
    unzip -q -o -B /opt/has.zip -d /opt/has && \
    rm -f /opt/has.zip

#PKG-INFO file must also exists in the conductor folder (i.e. besides and inside the of_has.egg-info folder). The zip file for distro above is missing it
RUN cp /opt/has/conductor/of_has.egg-info/PKG-INFO /opt/has/conductor
RUN pip install -e /opt/has/conductor

COPY app.wsgi /etc/nginx/conductor.wsgi
COPY api_paste.ini /usr/local/etc/conductor/api_paste.ini
