.. This work is licensed under a Creative Commons Attribution 4.0 International License.

Optimization Framework: Homing and Allocation
=============================================

OOF-HAS is an policy-driven placement optimizing service (or homing service) that allows ONAP to 
deploy services automatically across multiple sites and multiple clouds. 
It enables placement based on a wide variety of policy constraints including capacity, 
location, platform capabilities, and other service specific constraints. 

HAS is a distributed resource broker that enables automated policy-driven optimized placement of 
services on a global heterogeneous platform using ONAP. Given a set of service components 
(based on SO decomposition flows) and requirements for placing these components 
(driven by policies), HAS finds optimal resources (cloud regions or existing service instances) 
to home these service components such that it meets all the service requirements. 
HAS is architected as an extensible homing service that can accommodate a growing set of 
homing objectives, policy constraints, data sources and placement algorithms. It is also 
service-agnostic by design and can easily onboard new services with minimal effort. 
Therefore, HAS naturally extends to a general policy-driven optimizing placement platform 
for wider range of services, e.g., DCAE micro-services, ECOMP control loops, server capacity, etc. 
Finally, HAS provides an traceable mechanism for what-if analysis which is critical for ease of 
understanding a homing recommendation and resolving infeasibility scenarios.

.. toctree::
   :maxdepth: 1

   ./sections/architecture.rst
   ./sections/homingspecification.rst
   ./sections/offeredapis.rst
   ./sections/consumedapis.rst
   ./sections/delivery.rst
   ./sections/logging.rst
   ./sections/installation.rst
   ./sections/configuration.rst
   ./sections/administration.rst
   ./sections/humaninterfaces.rst
   ./sections/release-notes.rst

