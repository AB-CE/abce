Walk through
============

This tutorial is a step by step guide to create an agent-based model with ABCE.
In the following two text boxes, we the two concepts that make ABCE special are
explained: The explicit modeling of trade able goods. And the physical closeness
of the economy. (Which with some care leads to a general model - all in general
equilibrium. (Of cause without equilibrium)

.. sidebar:: Objects the other ontological object of agent-based models.

 Objects have a special stance in agent-based modeling:
    -  objects can be recovered (resources)
    -  exchanged (trade)
    -  transformed (production)
    -  consumed (transformed :-))
    -  destroyed (not really) and time depreciated

    ABCE, takes automatically care of Trade, production / transformation and consumption
    of goods. Good categories can also be made to perish or regrow. Services and
    renting can so be modeled.

 Closed economy
    When we impose that goods can only be transformed. The economy is physically
    closed (the economy is stock an flow consistent). When the markets are in a
    complete network our economy is complete. Think "general" in equilibrium
    economics.

    Caveats: If agents horde without taking their stock into account its
    like destruction.

With this basic understanding you can now start writing your own model.

To create a model you basically have to follow three steps:

    1. Specify endowments that replenish every round and goods / services
        that perish
    2. Specify the order of actions
    3. Write the agents with their actions

There is of course a little bit of admin you have to do:

    1. import agents in the model
    2. specify parameters



Have a look on the `abce/examples/` folder
------------------------------------------

It is instructive to look an a simple example, for example the 2x2 economy.
Than you can make a working copy of the template or a copy of an example.
(you need to change the `abce/lib` path in `start.py`)

Make a working copy
-------------------

1. copy abce/example to your_model_path::

    cd your_model_path
    cp ../abce/template/* .

2. In line 3 of `start.py`: adjust sys.path.append('your_path_to/abce/lib')

start.py
--------

Overview
~~~~~~~~

In start.py the simulation, thus the parameters, objects, agents and time line are
set up. Further it is declared, what is observed and written to the database. [#division]_

::

    from Firm import Firm
    from Household import Household

Here the Agent class Firm is imported from the file Firm.py. Likewise the Household class.



ABCE, reads the model parameter from a spreed sheet, every line is one simulation::

 for parameters in simulation.read_parameters('simulation_parameters.csv'):

    ...

With the parameters ABCE loops over the intended line, to create the simulation
and than runs the simulation. (after that it reads the next line an loops again).
The variable parameters contains all parameters from 'simulation_parameters.csv'.
See `simulation_parameters and agent_parameters` for details.

To set up a new model, you create a class a that will comprise your model::

    s = Simulation(parameters)

    ...

After this the order of actions, agents and objects are added.

::

    action_list = [
    ('Household', 'offer_capital'),

    ...

    ('Household', 'consumption')
    ]
    s.add_action_list(action_list)

This establishes the order of the simulation. It can also be read from file :meth:`abce.add_action_list_from_csv_file`

In order to add an agent which was imported before we simply build this agents::

        s.build_agents(Firm, 'number_of_firms')
        s.build_agents(Household, 10)

The number of firms to be build is read from the column in simulation_parameters.csv called number_of_firms.
The number of households on the other side is fixed at 10.

Goods are declared by goods classes. A normal good needs not to be declared. Below in the text you will
see how to declare, perishable goods and periodically renewed endowments (resources) [The goods]

Or you can create panel data for a group of agents::

    s.panel_db('Firm', command='after_sales_before_consumption')
    s.panel_db('Household')  # at the beginning
    ...

    s.run()

.. [#db_order] panal_db must be declared after the declaration of the agents.

The order of actions: The order of actions within a round
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every agents-based model is characterized by the order of which the actions are
 executed. In ABCE, there are rounds, every round is composed of sub-rounds, in
which all agents, a group of agents or a single agent, act in parallel. In the
code below you see a typical sub-round.

You have to declare an action_list, that is made of tuples telling ABCE which
agent or agent group, should execute which method::

    action_list = [
    repeat([
        ('Household', 'offer_capital'),
        ('Firm', 'buy_capital'),
    ],
    repetitions=10),
    ('Household', 'search_work'),
    ('Firm', 'hire_labor'),
    ('Firm', 'production'),
    'after_sales_before_consumption',
    ('Household', 'consumption')
    ]
    s.add_action_list(action_list)

The first tuple for example tells all Household agents to execute the method "offer_capital".
The 'after_sales_before_consumption' is a database command. see :meth:`abce.panel_db`.

The repeat function allows to repeat actions within the brackets a determinate amount of times.

Interactions happen between sub-rounds. An agent, sends a message in one round.
The receiving agent, receives the message the following sub-round.  A trade is
finished in three rounds: (1) an agent sends an offer the good is block, so it
can not be sold twice (2) the other agent accepts or rejects it. (3) If
accepted, the good is automatically delivered. If the trade was rejected: the
blocked good is unblocked.

The goods
~~~~~~~~~

A normal good can be traded and used for production or consumption.
The only thing you have to do is create the amount of goods for every agent with
:meth:`abceagent.Agent.create` in the agent's __init__ method.

If an agent receives and endowment every round this can be automatically handled,
with :meth:`abce.Simulation.declare_round_endowment`.
For example the following command gives every round who possess one unit of 'field'
on unit of 'corn' every round::

   s.declare_round_endowment('field', 100, 'corn')

You can also declare goods that last only one round and than automatically perish.
:meth:`abce.Simulation.declare_perishable` ::

    s.declare_perishable('corn')


This example declares 'corn' perishable and every round the agent gets 100 units of
of 'corn' for every unit of field he possesses. If the corn is not consumed, it
automatically disappears at the end of the round.

One important remark, for a logically consistent **macro-model** it is best to
not create any goods during the simulation, but only in
:meth:`abceagent.Agent.__init__`. During the simulation the only new goods
should be created by declare_round_endowment. In this way the economy is physically
closed. An exception is, of course, money.

The agents
----------

Agents are modeled in a separate file. In the template directory, you will find
three agents: agent.py, firm.py and household.py.

At the begin of each agent you will find::

    from __future__ import division

This sets python's division to floating point division instead of integer
division. Deleting this line, just asks for trouble.[#division]_

An agent has to import the :module:`abceagent` module and some helpers::

    import abceagent
    from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods

This imports the base classes: abceagent, Household and Firm.

An agent is a class and must at least inherit :class:`abceagent.Agent`
:class:`abceagent.Trade`, :class:`abceagent.Messaging` and :class:`abceagent.Database`
are automatically inherited::

    class Agent(abceagent.Agent):

To create an agent that can also consume::

    class Household(abceagent.Agent, abceagent.Household):

You see our Household agent inherits from abceagent, which is compulsory and Household.
Household an the other hand are a set of methods that are unique for Household agents.
(there is also a Firm class)

The __init__ method
~~~~~~~~~~~~~~~~~~~

::

    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abceagent.__init__(self, *_pass_to_engine)
        self.create('labor_endowment', 1)
        self.create('capital_endowment', 1)
        self.set_cobb_douglas_utility_function({"MLK": 0.300, "BRD": 0.700})
        self.prices = {}
        self.prices['labor'] = 1
        self.number_of_firms = simulation_parameters['number_of_firms']
        self.renter = random.randint(0, 100)
        self.last_utility = None


The __init__ method is the method that is called when the agents are created (by
the :meth:`abce.build_agents` or :meth:`abce.build_agents_from_file` method.)
In this method agents can access the simulation_parameters from the 'simulation_parameters.csv'.

If the agents are build using :meth:`abce.build_agents_from_file`. The agents
can access the parameters in their row, in 'agents_parameters.csv', by
agent_parameters in the __init__ function.

Line 2 is compulsory to pass the parameters to the abceagent.

With self.create the agent creates out of nothing the good 'labor_endowment'. Any
good can be created. Generally speaking. The __init__ method is the only place
where it is consistent to create a good. (except for money, if you simulate a naive
central bank).

This agent class inherited :meth:`abceagent.Household.set_cobb_douglas_utility_function`
from :class:`abceagent.Household`. With
:meth:`abceagent.Household.set_cobb_douglas_utility_function` you can create a
cobb-douglas function. Other functional forms are also available.

self.prices is a dictionary, created by the modeler, that saves prices for
specific goods. Here the price for labor is set to 1.

In order to let the agent remember a simulation_parameter it has to be saved in the self
domain the agent.  [#self]_

There is a random number assigned to self.renter and self.last_utility is initialized
with None. It is often necessary to initialize variable in the __init__ method to
avoid errors in the first round.

.. [#self] (self.number_of_firms = simulation_parameters['number_of_firms'])

The action methods and a consuming Household
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the other methods of the agent are executed when the corresponding sub-round is
called in start.py.  [#underscore]_

so when in the action list `('household', 'eat')` s called the eat method
is executed::

    class Agent(abceagent.Agent, abceagent.Household)
        def __init__(self):
            self.set_cobb_douglas_utility_function({'cookies': 0.9', 'bread': 0.1})
            self.create('cookies', 1)
            self.create('bread', 5)

    ...
    def eat(self):
        utility = self.consume_everything()
        self.log('utility', {'a': utility})



In the above example we see how a utility function is declared and and how and
agent consumes. The utility is logged and con be retrieved see
`Retrieval of the simulation results`

Firms and Production functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Firms do two things they produce (transform) and trade. [#joke]_ The following
code shows you how to declare a technology and produce brad from labor and
yeast.

::

    class Agent(abceagent.Agent, abceagent.Household):
    def init(self):
       set_cobb_douglas('BRD', 1.890, {"yeast": 0.333, "LAB": 0.667})
        ..
    def production(self):
        self.produce_use_everything()

More details in :class:`abceagent.Firm`. :class:`abceagent.FirmMultiFirm` offers
a more advanced interface for firms with complicated technologies.

Trade
~~~~~

ABCE handles trade fully automatically. That means, that goods are automatically
blocked and exchange. The modeler has only to decide when the agent offers a
trade and set the criteria to accept the trade::

    # Agent 1
    def selling(self):
        offerid = self.sell(buyer, 'BRD', 1, 2.5)
        self.checkorders.append(offerid)

    # Agent 2
    def buying(self):
        offers = self.get_offers('cookies')
        for offer in offers:
           try:
              self.accept(offer)
           except NotEnoughGoods:
              self.reject(offer)

You can find a detailed explanation how trade works is :class:`abceagent.Trade`

Data production
~~~~~~~~~~~~~~

There are three different ways of observing your agents:

Trade Logging
+++++++++++++

ABCE by default logs all trade and creates a SAM or IO matrix.

Manual in agent logging
+++++++++++++++++++++++

An agent can log a variable, :meth:`abceagent.Agent.possessions`, :meth:abceagent.Agent.possessions_all`
and must other methods such as :meth:`abceagent.Firm.produce` with :py:meth:`.log` or a
change in a variable with :py:meth:`.log_change`::

    self.log('possessions', self.possesions_all())
    self.log('custom', {'price_setting': 5: 'production_value': 12})
    prod = self.production_use_everything()
    self.log('current_production', prod)

Panel Data
++++++++++

:py:meth:`.panel_data` creates panel data for all agents in a specific
agent group at a specific point in every round. It is set in start.py::

    s.paneldb(’Household’, command=’aftersalesbeforeconsumption’)

The command has to be inserted in the action_list.

How to retrieve the Simulation results is explained in :ref:`simulation_results`

.. [#division] from __future__ import division, instructs python to handle division always as a
 floating point division. Use this in all your python code. If you do not use this ``3 / 2 = 1`` instead
 of ``3 / 2 = 1.5`` (floor division).

.. [#underscore] With the exception of methods, whose names start with a '_' underscore.underscoring methods that the agent uses only internally can speed up your code.

.. [#joke] We are aware that this is not entirely accurate, they also lobby to maximize their profit.

