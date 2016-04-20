.. _rsr:

Retrieval of the simulation results
===================================

Agents can log their internal states and the simulation can create
panel data. :mod:`abce.database`.

the results are stored in a subfolder of the ./results/ folder. The
exact path is in simulation.path. So if you want to post-process your
data, you can write a function that changes in to the simulation.path
directory and manipulates the CSV files there. The tables are stored
as '.csv' files which can be opened with excel.

The same data is also as a sqlite3 database 'database.db' available.
It can be opened by 'sqlitebrowser' in ubuntu.

Example::

    In start.py

    simulation = abce.Simulation(...)
    ...
    simulation.run()

    os.chdir(simulation.path)
    firms = pandas.read_csv('aggregate_firm.csv')
    ...
