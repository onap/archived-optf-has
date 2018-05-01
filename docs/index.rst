.. This work is licensed under a Creative Commons Attribution 4.0 International License.

Optimization Framework: Homing and Allocation
=============================================
The OOF provides a policy-driven and model-driven framework for creating optimization applications for a broad 
range of use cases.

It is being developed based on the following core ideas:

    1. Most optimization problems can be solved in a declarative manner using a high-level modeling language.

    2. Recent advances in open source optimization platforms allow the solution process to be mostly solver-independent.

    3. By leveraging the library of standard/global constraints, optimization models can be rapidly developed.

    4. By developing a focused set of platform components, we can realize a policy-driven, declarative system that allows ONAP optimization applications be composed rapidly and managed easily
        a. Policy and data adapters
        b. Execution and management environment
        c. Curated "knowledge base" and recipes to provide information on typical optimization examples and how to use the OOF 

    5. More importantly, by providing a way to support both "traditional" optimization applications and model-driven applications, we can provide a choice for users to adapt the platform based on their business needs and skills/expertise.


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

