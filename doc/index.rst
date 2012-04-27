.. ABCE documentation master file, created by
   sphinx-quickstart on Sat Apr 14 03:01:26 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ABCE's documentation!
================================

ABCE is a Python Agent-Based Complete Economy Protocol. Written by Davoud Taghawi-Nejad.


To write a ABCE model there are three steps:

 (1) define agent in AgentName.py using the 'Agent.py' prototype
 (2) modify this file
    (a) import agents
    (b) define action_list below [('which_agent', 'does_what'), ...]
    (c) define parameter suchs as the number_of_each_agent_type in parameter.csv
    (d) build_agents
    (e) declare some goods as resources

Further instructions contained in the files.




Contents:

.. toctree::
   :maxdepth: 4

   start
   agent

   world

   write

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

