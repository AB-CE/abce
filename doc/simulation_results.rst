Retrival of the simulation results
==================================

To recive a simulation::

 mysql -u abce -p
 --ictilo
 SHOW DATABASES;
 USE simulation_name_1204281421;
 SHOW TABLES;
 SELECT * FROM household_0;
 SELECT * FROM after_sales_before_consumption_firm ORDER BY round, id;
 DROP DATABASE simulation_name_1204281421;


There are also graphical tools, such as emma or SQL query browser
