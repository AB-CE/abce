abcEconomics the Agent-Based Computational Economy platform that makes modeling easier
//////////////////////////////////////////////////////////////////////////////////////

abcEconomics is a Python based modeling platform for economic simulations.
abcEconomics comes with standard functions to simulations of trade, production
and consumption. The modeler can concentrate on implementing
the logic and decisions of an agents; abcEconomics takes care of all exchange
of goods and production and consumption.

.. image:: https://zenodo.org/badge/4157636.svg
   :target: https://zenodo.org/badge/latestdoi/4157636

.. image:: https://travis-ci.org/AB-CE/abce.svg?branch=master
   :alt: abcEconomics build status on Travis CI
   :target: https://travis-ci.org/AB-CE/abce

.. image:: https://ci.appveyor.com/api/projects/status/c2w73u9im2b87reb?svg=true
   :alt: abcEconomics build status on Appveyor CI
   :target: https://ci.appveyor.com/project/AB-CE/abce

.. image:: https://img.shields.io/pypi/v/abcEconomics.svg
   :alt:  Pypi version
   :target: https://pypi.python.org/pypi/abcEconomics

.. image:: https://readthedocs.org/projects/abcEconomics/badge/?version=master
   :alt:  readthedocs
   :target: https://abcEconomics.readthedocs.io

.. figure:: https://raw.githubusercontent.com/AB-CE/abce/master/docs/cheesegrater.png
   :target: http://35.176.189.179/abcEconomics/
   :scale: 20 %
   :align: right

In abcEconomics, goods have the physical properties of
goods in reality in the sense that if agent A gives a good to agent B, then
- unlike information - agent B receives the good and agent B does not have
the good anymore.
The ownership and transformations (production or consumption) of goods are
automatically handled by the platform.

abcEconomics models are programmed in standard Python, stock functions of agents
can be inherited from archetype classes (Firm or Household). The only
not-so-standard Python is that agents are executed in parallel by the
Simulation class (in start.py).

abcEconomics allows the modeler to program agents as ordinary Python class-objects,
but run the simulation on a multi-core/processor computer. It takes no
effort or intervention from the modeler to run the simulation on a
multi-core system.
The speed advantages of using abcEconomics with multi-processes enabled.
abcEconomics are typically only observed for 10000 agents and more. Below, it
might be slower than pure python implementation. abcEconomics supports pypy3,
which is approximately 10 times faster than CPython.

abcEconomics is a scheduler and a set of agent classes.
According to the schedule the simulation class calls - each sub-round - agents
to execute some actions. Each agent executes these actions
using some of the build-in functions, such as trade, production and
consumption of abcEconomics. The agents can use the full set of commands of the
Python general purpose language.

The audience of abcEconomics are economists that want to model agent-based
models of trade and production.

abcEconomics does support an accounting framework
for financial simulations. `ESL can be downloaded here <https://github.com/AB-CE/abcESL>`_.

abcEconomics runs on macOS, Windows, and Linux. abcEconomics runs 10x faster on pypy!

Install with::

    pip3 install abcEconomics


The documentation is here:

    http://abce.readthedocs.io/

An example is here:

    `Insurance Market <http://35.176.189.179/abcEconomics/>`_

A code example is here:

    `Jupyter Tutorial <https://github.com/AB-CE/examples/tree/master/examples/jupyter_tutorial>`_

More code examples are here:

https://github.com/AB-CE/examples

