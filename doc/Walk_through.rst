Walk through / Tutorial
=======================

This tutorial is a step by step guide to create an agent-based model with ABCE.
In the following two text boxes, the two concepts that make ABCE special are
explained: The explicit modeling of tradeable goods and the optional concept
of a physically closed economy.

.. sidebar:: Objects the other ontological object of agent-based models.

 Objects have a special stance in agent-based modeling:
    -  objects can be recovered (resources)
    -  exchanged (trade)
    -  transformed (production)
    -  consumed
    -  destroyed (not really) and time depreciated

    ABCE, takes care of trade, production / transformation and consumption
    of goods automatically. Good categories can also be made to perish or regrow.

 Services or labor
    We can model services and labor as goods that perish
    and that are replenished every round. This would amount to a worker that can
    sell one unit of labor every round, that disappears if not used.

 Closed economy
    When we impose that goods can only be transformed. The economy is physically
    closed (the economy is stock and flow consistent). When the markets are in a
    complete network our economy is complete. Think "general" in equilibrium
    economics.

    Caveats: If agents horde without taking their stock into account it's
    like destruction.

With this basic understanding you can now start writing your own model.

To create a model you basically have to follow three steps:

    1. Specify endowments that replenish every round and goods / services that perish
    2. Specify the order of actions
    3. Write the agents with their actions

There is of course a little bit of administrative work you have to do:

    1. import agents in the model
    2. specify parameters



Have a look on the `abce/examples/` folder
------------------------------------------

It is instructive to look at a simple example, for example the 2x2 economy.
Then you can make a working copy of the template or a copy of an example.

Make a working copy
-------------------

copy abce/example to your_model_path::

    cd your_model_path
    cp path.to/abce/template/* .


start.py
--------

Overview
~~~~~~~~

In start.py the simulation, thus the parameters, objects, agents and time line are
set up. Further it is declared, what is observed and written to the database. [#division]_

::

    from abce import Simulation, gui
    from firm import Firm
    from household import Household

Here the Agent class Firm is imported from the file firm.py. Likewise the Household class.
Further the Simulation base class and the graphical user interface (gui) are imported




Parameters are specified as a python dictionary::

    simulation_parameters = {'name': 'name',
                             'trade_logging': 'off',
                             'random_seed': None,
                             'rounds': 40}


    @gui(simulation_parameters)
    def main(simulation_parameters):
        . . .

    if __name__ == '__main__':
        main(simulation_parameters)

The main function is generating and executing the simulation. When the main
function is preceded with "@gui(simulation_parameters)" The graphical user interface is executed
in your browser the simulation_parameters are used as default values. If now
browser window open you have to go manually to the
address "http://127.0.0.1:5000/". The graphical user interface can than start
the simulation.


To set up a new model, you create a class a that will comprise your model::

    s = Simulation(parameters)

    ...

After this the order of actions, agents and objects are added.

::

    action_list = [
    ('household', 'offer_capital'),
    (('firm', 'household'), 'buying')
    ...

    ('household', 'consumption')
    ]
    simulation.add_action_list(action_list)

This establishes the order of the simulation. Make sure you do not overwrite
internal abilities/properties of the agents. Such as 'sell', 'buy' or 'consume'.

In order to add an agent which was imported before we simply build these agents::

        simulation.build_agents(Firm, 'firm', number=simulation_parameters['number_of_firms'], parameters=simulation_parameters)
        simulation.build_agents(Household, 'household', number=10, parameters=simulation_parameters)

Each agent gets the simulation_parameters as first parameter in th init function.

Or you can create panel data for a group of agents::

    simulation.panel('Firm', command='after_sales_before_consumption')
    simulation.panel('Household')  # at the beginning
    ...

    simulation.run()


This only initializes the panel data. In the action list you must instruct the
agents to record panel data every round:

::

    (('firm', 'household'), 'panel'),


Similar you can also record aggregate data using 'simulation.aggregate' and
(('firm', 'household'), 'aggregate'),

.. [#db_order] panel must be declared before the declaration of the agents.

The order of actions: The order of actions within a round
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every agents-based model is characterized by the order of which the actions are executed.
In ABCE, there are rounds, every round is composed of sub-rounds, in which a group or
several groups of agents act in parallel. In the
code below you see a typical sub-round.

You have to declare an action_list, that is made of tuples telling ABCE which
agent or agent group, should execute which method::

    action_list = [
    repeat([
        ('household', 'offer_capital'),
        ('firm', 'buy_capital'),
    ],
    repetitions=10),
    (('firm', 'household', 'aggregate'))
    ('household', 'search_work'),
    ('firm', 'hire_labor'),
    ('firm', 'production'),
    (('firm', 'household'), 'after_sales_before_consumption'),
    ('Household', 'consumption')
    ]
    simulation.add_action_list(action_list)

The first tuple for example tells all household agents to execute the method "offer_capital".

The repeat function allows repeating actions within the brackets a determinate amount of times.

Interactions happen between sub-rounds. An agent, sends a message in one round.
The receiving agent, receives the message the following sub-round.  A trade is
finished in three rounds: (1) an agent sends an offer the good is blocked, so it
can not be sold twice (2) the other agent accepts or rejects it. (3) If
accepted, the good is automatically delivered at the beginning of the sub-round.
If the trade was rejected: the blocked good is automatically unblocked.

The goods
~~~~~~~~~

A good can be traded and used for production or consumption.
The only thing you have to do is create the amount of goods for every agent with
:meth:`abce.Agent.create` in the agent's init method.

If an agent receives an endowment every round this can be automatically handled,
with :meth:`abce.Simulation.declare_round_endowment`.
For example the following command gives, at the beginning of every round,
to whom who possess one unit of 'field' 100 units of 'corn'::

   simulation.declare_round_endowment('field', 100, 'corn')

You can also declare goods that last only one round and then automatically perish.
:meth:`abce.Simulation.declare_perishable` ::

    simulation.declare_perishable('corn')


This example declares 'corn' perishable and every round the agent gets 100 units of
of 'corn' for every unit of field he possesses. If the corn is not consumed, it
automatically disappears at the end of the round.

One important remark, for a logically consistent **macro-model** it is best to
not create any goods during the simulation, but only in
:meth:`abce.Agent.init`. During the simulation the only new goods
should be created by declare_round_endowment. In this way the economy is physically
closed.

The agents
----------

Agents are modeled in a separate file. In the template directory, you will find
three agents: agent.py, firm.py and household.py.

At the beginning of each agent you will again find::

    from __future__ import division


An agent has to import the :mod:`abce` module and some helpers::

    import abce
    from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods

This imports the module abce in order to use the base classes Household and Firm.

An agent is a class and must at least inherit :class:`abce.Agent`.
:class:`abce.Trade` - :class:`messaging.Messaging` and :class:`database.Database`
are automatically inherited::

    class Agent(abce.Agent):

To create an agent that can also consume::

    class Household(abce.Agent, abce.Household):

You see our Household agent inherits from :class:`abce.Agent`, which is compulsory and :class:`abce.Household`.
Household on the other hand are a set of methods that are unique for Household agents.
(there is also a Firm class)

The init method
~~~~~~~~~~~~~~~~~~~

**DO NOT OVERWRITE THE __init__ method. Instead use ABCE's init method**

::

    def init(self, simulation_parameters, agent_parameters):
        self.create('labor_endowment', 1)
        self.create('capital_endowment', 1)
        self.create('money', 1)
        self.set_cobb_douglas_utility_function({"MLK": 0.300, "BRD": 0.700})
        self.prices = {}
        self.prices['labor'] = 1
        self.number_of_firms = simulation_parameters['number_of_firms']
        self.renter = random.randint(0, 100)
        self.last_utility = None


The init method is the method that is called when the agents are created (by
the :meth:`abce.Simulation.build_agents`)
In this method agents can access the simulation_parameters given as parameters or
agents_parameters.

If you build_agents and give a dictionary as `parameter`, the content of this will be made
available to all agents. If you specify agents_parameters, which must be a list,
then each agent gets one element of this list.

With self.create the agent creates the good 'labor_endowment'. Any
good can be created. Generally speaking. In order to have a phisically consistent
economy goods should only be created in the init method. The good money is used
in transactions.

This agent class inherited :meth:`abce.Household.set_cobb_douglas_utility_function`
from :class:`abce.Household`. With
:meth:`abce.Household.set_cobb_douglas_utility_function` you can create a
cobb-douglas function. Other functional forms are also available.

In order to let the agent remember a simulation_parameter it has to be saved in the self
domain the agent.

The action methods and a consuming Household
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the other methods of the agent are executed when the corresponding sub-round is
called from the Simulation set up in start.py.  [#underscore]_

For example when in the action list `('household', 'eat')` is called the eat method
is executed of each household agent is executed::

    class Agent(abce.Agent, abce.Household)
        def init(self):
            self.set_cobb_douglas_utility_function({'cookies': 0.9', 'bread': 0.1})
            self.create('cookies', 1)
            self.create('bread', 5)

        ...
        def eat(self):
            utility = self.consume_everything()
            self.log('utility', {'a': utility})



In the above example we see how a utility function is declared and how the
agent consumes. The utility is logged and can be retrieved see
:ref:`retrieval of the simulation results <rsr>`

Firms and Production functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Firms do two things they produce (transform) and trade. The following
code shows you how to declare a technology and produce bread from labor and
yeast.

::

    class Agent(abce.Agent, abce.Household):
        def init(self):
           set_cobb_douglas('BRD', 1.890, {"yeast": 0.333, "LAB": 0.667})
            ...

        def production(self):
            self.produce_use_everything()

More details in :class:`abce.Firm`. :class:`abce.FirmMultiTechnologies` offers
a more advanced interface for firms with complicated technologies.

Trade
~~~~~

ABCE handles trade fully automatically. That means, that goods are automatically
exchanged, double selling of a good is avoided by subtracting a good from
the possessions when it is offered
for sale. The modeler has only to decide when the agent offers a
trade and sets the criteria to accept the trade::

    # Agent 1
    def selling(self):
        offerid = self.sell(buyer, 'BRD', 1, 2.5)
        self.checkorders.append(offerid)  # optional

    # Agent 2
    def buying(self):
        offers = self.get_offers('cookies')
        for offer in offers:
           try:
              self.accept(offer)
           except NotEnoughGoods:
              self.reject(offer)

You can find a detailed explanation how trade works in :class:`abce.Trade`

Data production
~~~~~~~~~~~~~~~

There are three different ways of observing your agents:

Trade Logging
+++++++++++++

ABCE by default logs all trade and creates a SAM or IO matrix.
This matrixes are currently not display in the GUI, but
accessible as csv files in the `simulation.path` directory

Manual in agent logging
+++++++++++++++++++++++

An agent can log a variable, :meth:`abce.Agent.possessions`, :meth:`abce.Agent.possessions_all`
and most other methods such as :meth:`abce.Firm.produce` with :py:meth:`abce.Agent.log` or a
change in a variable with :py:meth:`.log_change`::

    self.log('possessions', self.possesions_all())
    self.log('custom', {'price_setting': 5: 'production_value': 12})
    prod = self.production_use_everything()
    self.log('current_production', prod)

Panel Data
++++++++++

:py:meth:`.panel_data` creates panel data for all agents in a specific
agent group at a specific point in every round. It is set in start.py::

    simulation.panel(’Household’, variables='goodA')

A command has to be inserted in the action_list::

    ('household', 'panel')

Retrieving the logged data
++++++++++++++++++++++++++

the results are stored in a subfolder of the ./results/ folder.
simulation.path gives you the path to the folder.

The tables are stored as '.csv' files which can be opened with excel.
Further you can import the files with R:

 1. change to the subfolder of ./results/ that contains your simulation
    results
 2. start R
 3. `load('database.R')`

.. [#division] from __future__ import division, instructs python to handle division always as a
 floating point division. Use this in all your python code. If you do not use this ``3 / 2 = 1`` instead
 of ``3 / 2 = 1.5`` (floor division).

.. [#underscore] With the exception of methods, whose names start with a '_' underscore.underscoring methods that the agent uses only internally can speed up your code.

.. [#joke] We are aware that this is not entirely accurate, they also lobby to maximize their profit.

