#!/bin/bash
#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
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
#
#docker run -d --name aaisim -p 8081:8081  aaisim
docker run --name aaisim -p 2525:2525 -p 8081:8081 -d andyrbell/mountebank:2.3.2

sleep 10

#generate imposter data
python3 imposter.py aaisim/aai_imposter.jsont aaisim/responses aai_imposter.json

#Add imposter at 8081
curl -i -X POST -H 'Content-Type: application/json' http://localhost:2525/imposters --data @aai_imposter.json

rm -rf aai_imposter.json
