.. Agent-Based Computational Economics documentation master file, created by
   sphinx-quickstart on Mon Sep  4 18:00:57 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


ABCE the Agent-Based Computational Economy platform that makes modeling easier
//////////////////////////////////////////////////////////////////////////////

ABCE is a Python Agent-Based Computational Economy Platform, written by Davoud Taghawi-Nejad.
The impatient reader can jump directly to the 'Interactive jupyter / IPython notebook Tutorial',
which explains how to set up a simulation. In the walk through you will learn how to set up an agent
and how to trade with other agents. The Household and Firm classes allow to
produce with different production functions and consume with utility functions.
But models don't have to use neoclassical assumptions. ABCE does support an accounting framwork
for financial simulations. `ESL can be downloaded here<https://github.com/AB-CE/ABCESL>`_.

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
   FirmMultiTechnologies
   MultiCurrencyTrade
   Quote
   spatial
   plugins

Graphical User Interface and Results
====================================
.. toctree::
   :maxdepth: 1

   gui
   files
   deploy





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
