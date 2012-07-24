Retrival of the simulation results
==================================

Agents can log their internal states and the simulation can create
panel data. :class:`abceagent.Database`.

the results are stored in a subfolder of the ./results/ folder.

The tables are stored as '.csv' files which can be opened with excel and
libreoffice.
Further you can import the files with R, which also gives you a social
accounting matix:

 1. start a in the subfolder of ./results/ that contains your simulation
 	results
 2. start R
 3. `source('../../sam.R')`
 4. sam(t=0)

The same data is also as a sqlite database 'database.db' available.
It can be opened by 'sqlitebrowser' in ubuntu.
