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
ENV APP_USER "onap"
ENV APP_GROUP "onap"

RUN addgroup -S $APP_GROUP && adduser -S -G $APP_USER $APP_GROUP

# Creete the required directories
RUN mkdir -p /etc/nginx/ssl && \
    mkdir -p /var/log/conductor && \
    mkdir -p /run/conductor && \
    mkdir -p /run/nginx

# Install the required libraries
RUN apk --update add py-setuptools && \
    apk add unzip && \
    apk add curl && \
    apk add wget && \
    apk add fcgiwrap && \
    apk add bash vim && \
    apk add nginx && \
    apk add py2-pip libpq python-dev && \
    pip install --upgrade pip && \
    apk add --virtual build-dependencies build-base linux-headers pcre-dev libffi-dev libxslt-dev libressl-dev && \
    pip install uwsgi

# Get, Install, cleanup and setup
COPY onap-has-tm/optf-has-conductor-${MVN_ARTIFACT_VERSION}.zip /tmp/optf-has.zip
RUN unzip -q -o -B /tmp/optf-has.zip -d /opt/has && rm -f /tmp/optf-has.zip

#PKG-INFO file must also exists in the conductor folder (i.e. besides and inside the of_has.egg-info folder). The zip file for distro above is missing it
RUN cp /opt/has/conductor/of_has.egg-info/PKG-INFO /opt/has/conductor
RUN pip install -e /opt/has/conductor
COPY app.wsgi /etc/nginx/conductor.wsgi
COPY api_paste.ini /usr/local/etc/conductor/api_paste.ini

# Set ownership to application user
RUN chown $APP_USER:$APP_GROUP -R /opt/has/ /var/log/
USER $APP_USER
