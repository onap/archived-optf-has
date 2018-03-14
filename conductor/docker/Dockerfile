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
ENV CON_ADDR "127.0.0.1"
ENV CON_PORT "8091"

EXPOSE 8091

RUN apt-get update && apt-get --assume-yes install python-setuptools && \
apt-get install -y unzip && \
apt-get install -y curl && \
apt-get install -y wget 

RUN git clone https://gerrit.onap.org/r/optf/has
RUN cd ./has/conductor/ && pip install -e .
COPY api_paste.ini /usr/local/bin/api_paste.ini
