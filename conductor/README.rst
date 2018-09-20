#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2018 AT&T Intellectual Property
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

=========
Conductor
=========

Conductor is the implementation of the Homing Service.

Given the description of what needs to be deployed (demands) and the placement requirements (constraints), Conductor determines placement candidates that meet all constraints while optimizing the resource usage of the AIC infrastructure. A customer request may be satisfied by deploying new VMs in AIC (AIC inventory) or by using existing service instances with enough remaining capacity (service inventory).

The formal project name is *Conductor*. From a canonical standpoint, Conductor is known as a *homing service*, in the same way OpenStack Heat is an orchestration service, or Nova is a compute service. References to *Homing Conductor* are a misnomer. Instead, refer to the project name (Conductor) or the canonical name (homing service).

* Free software: License TBD
* `PyPI`_ - package installation
* `Python/Linux Distribution Notes`_
* `Conductor Template Guide`_
* `Example Templates`_
* `Homing API`_
* `Bugs`_ - issue tracking
* `Source`_

