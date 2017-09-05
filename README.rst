============
Introduction
============

ABCE is a Python based modeling platform for economic simulations. For simulations of trade, production, and consumption, ABCE comes with standard functions that implement these kinds of interactions and actions. The modeler only implements the logic and decisions of the agents; ABCE takes care of all exchange of goods and production and consumption.

.. figure:: http://abce.readthedocs.io/en/0.9b/_images/cheesegrater.png
   :target: http://35.176.189.179/ABCE/
   :figwidth: 50 %
   :align: rightg

One special feature of ABCE is that goods have the physical properties of goods in reality. In other words, if agent A gives a good to agent B, then - unlike information - agent B receives the good and agent B does not have the good anymore. That means that agents can trade, produce or consume a good. The ownership and transformations (production or consumption) of goods are automatically handled by the platform.

ABCE models are programmed in standard Python, stock functions of agents are inherited from archetype classes (Agent, Firm or Household). The only not-so-standard Python is that agents are executed in parallel by the Simulation class (in start.py).

 ABCE does support an accounting framwork for financial simulations: ABCESL can be downloaded [here](https://github.com/AB-CE/ABCESL).


.. image:: https://zenodo.org/badge/4157636.svg
   :target: https://zenodo.org/badge/latestdoi/4157636

.. image:: https://travis-ci.org/AB-CE/abce.svg?branch=master
   :alt: ABCE build status on Travis CI
   :target: https://travis-ci.org/AB-CE/abce

.. image:: https://ci.appveyor.com/api/projects/status/c2w73u9im2b87reb?svg=true
   :alt: ABCE build status on Appveyor CI
   :target: https://ci.appveyor.com/project/AB-CE/abce

.. image:: https://img.shields.io/pypi/v/abce.svg
   :alt:  Pypi version
   :target: https://pypi.python.org/pypi/abce

.. image:: https://readthedocs.org/projects/abce/badge/?version=master
   :alt:  readthedocs
   :target: https://abce.readthedocs.io


Install with:

    python3 -m pip install abce

The documentation is here:

[http://abce.readthedocs.io/](http://abce.readthedocs.io/)

An example is here:

[Insurance Market](http://35.176.189.179/ABCE/)

A code example is here:

[Jupytor Tutorial](https://github.com/AB-CE/examples/tree/master/examples/jupyter_tutorial)

More code examples are here:

[(https://github.com/AB-CE/examples]((https://github.com/AB-CE/examples)
