Examples
========

abcEconomics's examples can be downloaded from here: https://github.com/AB-CE/examples

Concepts used in examples
-------------------------

+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| Example                | jupyter | pandas | logging | Trade   | multi- | create | delete | graphical | endowment | perishable | mesa      | contracts |
|                        |         |        |         |         | core   | agents | agents | user      |           |            | graphical |           |
|                        |         |        |         |         |        |        |        | interface |           |            | spacial   |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| jupyter_tutorial       | X       | X      | X       | X       |        |        |        |           |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| 50000_firms            |         |        |         |         | X      |        |        |           |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| create_agents          |         |        |         |         |        | X      |        |           |           |            |           |           |
| delete_agent           |         |        |         |         |        |        | X      |           |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| one_household_one_firm |         |        |         |         |        |        |        | X         |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| .. with_logic          |         |        |         |         |        |        |        |           | X         | X          |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| pid_controller         |         |        |         | X       |        |        |        |           |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| mesa_example           |         |        |         |         |        |        |        |           |           |            | X         |           |
| sugarscape             |         |        |         |         |        |        |        |           |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| CCE                    |         | X      |         | trade   |        |        |        |  Extended |           |            |           |           |
|                        |         |        |         | logging |        |        |        | GUI       |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| cheesegrater insurance |         |        |         |         |        |        |        | X         |           |            |           | X         |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| 2sectors               |         |        |         |         |        |        |        |           |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+
| Model of Car market    |         |        |         |         |        |        |        |           |           |            |           |           |
+------------------------+---------+--------+---------+---------+--------+--------+--------+-----------+-----------+------------+-----------+-----------+


+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| Example                | production | utility  | arbitrary        | multi- | create | delete | graphical | endowment | perishable | mesa      |
|                        | function   | function | time intervals   | core   | agents | agents | user      |           |            | graphical |
|                        |            |          |                  |        |        |        | interface |           |            | spacial   |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| jupyter_tutorial       |            |          |                  |        |        |        |           |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| 50000_firms            |            |          |                  | X      |        |        |           |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| create_agents          |            |          |                  |        | X      |        |           |           |            |           |
| delete_agent           |            |          |                  |        |        | X      |           |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| one_household_one_firm |            |          |                  |        |        |        | simple    |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| .. with_logic          |            |          |                  |        |        |        |           | X         | X          |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| pid_controller         |            |          |                  |        |        |        |           |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| mesa_example           |            |          |                  |        |        |        |           |           |            | X         |
| sugarscape             |            |          |                  |        |        |        |           |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| CCE                    | X          | X        |                  |        |        |        | X         |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| cheesegrater insurance |            |          |                  |        |        |        | X         |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| 2sectors               | X          | X        |                  |        |        |        |           |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| Model of Car market    |            |          |                  |        |        |        |           |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+
| Calendar               |            |          | X                |        |        |        |           |           |            |           |
+------------------------+------------+----------+------------------+--------+--------+--------+-----------+-----------+------------+-----------+


Models
------

CCE
```

This is the most complete example featuring an agent-based model of climate change tax policies for
the United States. It includes a GUI, is databased and and uses production and utility functions.

One sector model
````````````````


One household one firm is a minimalistic example of a 'macro-economy'.
It is 'macro' in the sense that the complete circular flow of the economy is
represented. Every round the following sub-rounds are executed:

        household:
            sell_labor
        firm:
            buy_labor
        firm:
            production
        firm:
            sell_goods
        household:
            buy_goods
        household:
            consumption

After the firms' production and the acquisition of goods by the household
a statistical panel of the firms' and the households' possessions, respectively,
is written to the database.

The economy has two goods a representative 'GOOD' good and 'labor' as
well as money. 'labor', which is a service that is represented as a good that
perishes every round when it is not used. Further the endowment is
of the labor good that is replenished every round for every agent that
has an 'adult'. 'Adults' are handled like possessions of the household agent.

The household has a degenerate Cobb-Douglas utility function and the firm
has a degenerate Cobb-Douglas production function:

::

    utility = GOOD ^ 1

    GOOD = labor ^ 1

The firms own an initial amount of money of 1 and the household
has one adult, which supplies one unit of (perishable) labor every
round.

First the household sells his unit of labor. The firm buys this unit
and uses all available labor for production. The complete production
is offered to the household, which in turn buys everything it can afford.
The good is consumed and the resulting utility logged to the database.

Two sector model
````````````````

The two sector model is similar to the one sector model. It has two
firms and showcases abcEconomics's ability to control the creation of agents
from an excel sheet.

There are two firms. One firm manufactures an intermediary good. The
other firm produces the final good. Both firms are implemented with
the same good. The type a firm develops is based on the excel sheet.

The two respective firms production functions are:

::

    intermediate_good = labor ^ 1

    consumption_good = intermediate_good ^ 1 * labor ^ 1

The only difference is that, when firms sell their products the
intermediate good firm sells to the final good firm and the final
good firm, in the same sub-round sells to the household.

In start.py we can see that the firms that are build are build
from an excel sheet:

    w.build_agents_from_file(Firm, parameters_file='agents_parameters.csv')
    w.build_agents_from_file(Household)

And here the excel sheet:

    agent_class number  sector
    firm        1   intermediate_good
    firm        1   consumption_good
    household   1   0
    household   1   1

The advantage of this is that the parameters can be used in the agent.
The line `self.sector = agent_parameters['sector']` reads the sector
column and assigns it to the self.sector variable. The file simulation
parameters is read - line by line - into the variable simulation_parameters.
It can be used in start.py and in the agents with
simulation_parameters['columnlabel'].

50000 agents example
````````````````````

This is a sheer speed demonstration, that lets 50000 agents trade.

PID controllers
```````````````

PID controller are a simple algorithm for firms to set prices and
quantities. PID controller, work like a steward of a ship. He
steers to where he wants to go and after each action corrects
the direction based on how the ship changed it's direction,

pid_controller analytical
+++++++++++++++++++++++++

A simulation of the first Model of Ernesto Carrella's paper:
Sticky Prices Microfoundations in a Agent Based Supply Chain
Section 4 Firms and Production

Here we have one firm and one market agent. The market agent
has the demand function q = 102 - p. The PID controller uses
an analytical model of the optimization problem.

Simple Seller Example
+++++++++++++++++++++

A simulation of the first Model of Ernesto Carrella's paper: Zero-Knowledge Traders,
journal of artificial societies and social simulation, December 2013

This is a partial 'equilibrium' model. A firm has a fixed production of 4 it offers
this to a fixed population of 10 household. The household willingness to pay is
household id * 10 (10, 20, 30 ... 90).
The firms sets the prices using a PID controller.

Fully PID controlled
++++++++++++++++++++

A simulation of the first Model of Ernesto Carrella's paper:
Sticky Prices Microfoundations in a Agent Based Supply Chain
Section 4 Firms and Production

Here we have one firm and one market agent. The market agent
has the demand function q = 102 - p. The PID controller
has no other knowledge then the reaction of the market in
terms of demand.

