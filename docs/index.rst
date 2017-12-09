.. Agent-Based Computational Economics documentation master file, created by
   sphinx-quickstart on Mon Sep  4 18:00:57 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


ABCE the Agent-Based Computational Economy platform that makes modeling easier
//////////////////////////////////////////////////////////////////////////////

ABCE is a Python based modeling platform for economic simulations.
ABCE comes with standard functions to simulations of trade, production
and consumption. The modeler can concentrate on implementing
the logic and decisions of an agents; ABCE takes care of all exchange
of goods and production and consumption.

.. figure:: cheesegrater.png
   :figwidth: 50 %
   :align: right

In ABCE  goods have the physical properties of
goods in reality in the sense that if agent A gives a good to agent B, then
- unlike information - agent B receives the good and agent B does not have
the good anymore.
The ownership and transformations (production or consumption) of goods are
automatically handled by the platform.

ABCE models are programmed in standard Python, stock functions of agents
can be inherited from archetype classes (Firm or Household). The only
not-so-standard Python is that agents are executed in parallel by the
Simulation class (in start.py).

ABCE allows the modeler to program agents as ordinary Python class-objects,
but run the simulation on a multi-core/processor computer. It takes no
effort or intervention from the modeler to run the simulation on a
multi-core system.
The speed advantages of using ABCE with multi-processes enabled.
ABCE are typically only observed for 10000 agents and more. Below, it
might be slower than pure python implementation. ABCE supports pypy3,
which is approximately 10 times faster than CPython.

ABCE is a scheduler [#scheduler]_ and a set of agent classes.
According to the schedule the simulation class calls - each sub-round - agents
to execute some actions. Each agent executes these actions
using some of the build-in functions, such as trade, production and
consumption of ABCE. The agents can use the full set of commands of the
Python general purpose language.

The audience of ABCE are economists that want to model agent-based
models of trade and production.

ABCE does support an accounting framework
for financial simulations. `ESL can be downloaded here <https://github.com/AB-CE/ABCESL>`_.

ABCE runs on macOS, Windows, and Linux. ABCE runs 10x faster on pypy!



Introduction
============
.. toctree::
   :maxdepth: 2

   introduction
   installation
   jupyter_tutorial
   Walk_through
   tutorial
   examples
   unit_testing

Simulation Programming
======================
.. toctree::
   :maxdepth: 1

   simulation
   Agent_class
   Goods
   Trade
   Messaging
   Firm
   Household
   Database
   notenoughgoods


Advanced
========
.. toctree::
   :maxdepth: 1

   Contracting
   Quote
   spatial
   plugins

Graphical User Interface and Results
====================================
.. toctree::
   :maxdepth: 1

   gui
   deploy





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. [#scheduler] the Simulation class
.. [#noeq] with out the equilibrium of course
