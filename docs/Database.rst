Observing agents and logging
============================

.. default-domain::abcEconomics.database.Database


There are different ways of observing your agents:

Trade Logging:
	abcEconomics by default logs all trade and creates a SAM or IO matrix.

Manual in agent logging:
	An agent is instructed to log a variable with :py:meth:`.log` or a
	change in a variable with :py:meth:`.log_change`.

Aggregate Data:
    :py:meth:`.aggregate` save agents possessions and variable aggregated
    over a group

Panel Data:
	:py:meth:`.panel` creates panel data for all agents in a specific
	agent group at a specific point in every round. It is set in start.py

How to retrieve the Simulation results is explained in retrieval_


Trade Logging
~~~~~~~~~~~~~

By default abcEconomics logs all trade and creates a social accounting matrix or
input output matrix. Because the creation of the trade log is very time consuming
you can change the default behavior in world_parameter.csv. In the column
'trade_logging' you can choose 'individual', 'group' or 'off'. (Without the
apostrophes!).

Manual logging
~~~~~~~~~~~~~~

All functions except the trade related functions can be logged. The following
code logs the production function and the change of the production from last
year::

 output = self.produce(self.inputs)
 self.log('production', output)
 self.log_change('production', output)

Log logs dictionaries. To log your own variable::

 self.log('price', {'input': 0.8, 'output': 1})

Further you can write the change of a variable between a start and an end point with:
:py:meth:`.observe_begin` and :py:meth:`.observe_end`.

.. autoclass:: abcEconomics.database.Database
    :members:
    :show-inheritance:

Panel Data
~~~~~~~~~~

.. automethod:: abcEconomics.group.Group.panel_log

Aggregate Data
~~~~~~~~~~~~~~

.. automethod:: abcEconomics.group.Group.agg_log


.. _retrieval:


Retrieval of the simulation results
===================================

Agents can log their internal states and the simulation can create
panel data. :mod:`abcEconomics.logger`.

the results are stored in a subfolder of the ./results/ folder. The
exact path is in simulation.path. So if you want to post-process your
data, you can write a function that changes in to the simulation.path
directory and manipulates the CSV files there. The tables are stored
as '.csv' files which can be opened with excel.

The same data is also as a sqlite3 database 'database.db' available.
It can be opened by 'sqlitebrowser' in ubuntu.

Example::

    In start.py

    simulation = abcEconomics.Simulation(...)
    ...
    simulation.run()

    os.chdir(simulation.path)
    firms = pandas.read_csv('aggregate_firm.csv')
    ...

