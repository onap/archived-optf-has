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
RUN apt-get update
RUN apt-get --assume-yes install python-setuptools
RUN virtualenv ../venv
RUN git clone https://gerrit.onap.org/r/optf/has
WORKDIR ./conductor
RUN pip install .
RUN pwd
RUN echo "Starting conductor-controller"
CMD ["python","/usr/local/bin/conductor-controller", "--config-file=/usr/local/bin/conductor.conf"]
