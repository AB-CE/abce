Observing agents
================

.. default-domain::agentengine.Database
.. default-domain::worldengine.WorldEngine


There are three different ways of observing your agents:

Trade Logging
	ABCE by default logs all trade and creates a SAM or IO matrix.
Manual in agent logging
	An agent is instructed to log a variable with :py:meth:`.log` or a
	change in a variable with :py:meth:`.log_change`.
Panel Data
	:py:meth:`.panel_data` creates panel data for all agents in a specific
	agent group at a specific point in every round. It is set in start.py

How to retrieve the Simulation results is explained in :doc:`simulation_results`


Trade Logging
~~~~~~~~~~~~~

By default ABCE logs all trade and creates a social accounting matrix or
input output matrix. Because the creation of the trade log is very time consuming
you can change the default behavior in world_parameter.csv. In the column
'trade_logging' you can choose 'individual', 'group' or 'off'. (Without the
apostrophs!).

Manual logging
~~~~~~~~~~~~~~

All functions except the trade related functions can be logged. The following
code logs the production function and the change of the production from last
year::

 output = self.produce(self.inputs)
 self.log('production', output)
 self.log_change('production', output)

Log loggs dictionaries. To log your own variable::

 self.log('price', {'input': 0.8, 'output': 1})

Further you can write the change of a varibale between a start and an end point with:
:py:meth:`.observe_begin` and :py:meth:`.observe_end`.

.. autoclass:: abceagent.Database
    :members:
    :show-inheritance:

Panel Data
~~~~~~~~~~

.. automethod:: abce.Simulation.panel_data


