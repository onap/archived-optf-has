# Conductor

OF-HAS is the implementation of the ONAP Homing Service. The formal project name in ONAP is *OF-HAS*. The informal name for the project is *Conductor* (inherited from the seed-code), which is interchangeably used through the project.

Given the description of what needs to be deployed (demands) and the placement requirements (constraints), Conductor determines placement candidates that meet all constraints while optimizing the resource usage of the AIC infrastructure. A customer request may be satisfied by deploying new VMs in AIC (AIC inventory) or by using existing service instances with enough remaining capacity (service inventory).

From a canonical standpoint, Conductor is known as a *homing service*, in the same way OpenStack Heat is an orchestration service, or Nova is a compute service.

* License: Licensed under the Apache License, Version 2.0
* [PyPI]() - package installation
* [Python/Linux Distribution Notes](/doc/distribution/README.md)
* [Conductor Template Guide](/doc/template/README.md)
* [Example Templates](/doc/examples/README.md)
* [Homing API](/doc/api/README.md)
* [Bugs](https://jira.onap.org/projects/OPTFRA/summary) - issue tracking
* [Source](https://gerrit.onap.org/r/optf/has)
