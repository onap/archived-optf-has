=========
Conductor
=========

Conductor is the implementation of the ECOMP Homing Service.

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

.. _PyPI: http://jldv0006.jadc.att.com:8093/nexus/#browse/browse/components:pypi-hosted:e5c50d09b73fd3c579f00fba903ebf40
.. _Python/Linux Distribution Notes: https://codecloud.web.att.com/projects/ST_CLOUDQOS/repos/conductor/browse/doc/distribution/README.md
.. _Conductor Template Guide: https://codecloud.web.att.com/projects/ST_CLOUDQOS/repos/conductor/browse/doc/template/README.md
.. _Example Templates: https://codecloud.web.att.com/projects/ST_CLOUDQOS/repos/conductor/browse/doc/examples/README.md
.. _Homing API: https://codecloud.web.att.com/projects/ST_CLOUDQOS/repos/conductor/browse/doc/api/README.md
.. _Bugs: https://itrack.web.att.com/browse/CQOS-22?jql=project%20%3D%20CQOS%20AND%20component%20%3D%20Conductor
.. _Source: https://codecloud.web.att.com/projects/ST_CLOUDQOS/repos/conductor

Note: The following line is required by Nexus/AAF (AT&T Intranet).

aaf_namespace = com.att.ecomp.conductor
