Walk through
============

In order to learn using ABCE we will now dissect and explain a simple ABCE model.
Additional to this walk through you should also have a look on the examples in
the `abce/examples/` folder,


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


start.py
--------

    .. code-block:: python

        """ 1. declared the timeline
            2. build one Household and one Firm follow_agent
            3. For every labor_endowment an agent has he gets one trade or usable labor
            per round. If it is not used at the end of the round it disapears.
            4. Firms' and Households' possessions are monitored ot the points marked in
            timeline.
        """

        from __future__ import division
        from abce import Simulation, gui
        from firm import Firm
        from household import Household

        parameters = {'name': '2x2',
                      'random_seed': None,
                      'rounds': 10}

        #@gui(parameters)
        def main(parameters):
            simulation = Simulation(rounds=parameters['rounds'])

            simulation.declare_round_endowment(resource='labor_endowment', units=1, product='labor')
            simulation.declare_perishable(good='labor')

            simulation.panel('household', possessions=['money', 'GOOD'],
                                 variables=['current_utiliy'])
            simulation.panel('firm', possessions=['money', 'GOOD'])

            firms = simulation.build_agents(Firm, 'firm', 1)
            households = simulation.build_agents(Household, 'household', 1)

            for round in simulation.next_round():
                households.do('sell_labor'),
                firms.do('buy_labor'),
                firms.do('production'),
                (households + firms).do('panel'),
                firms.do('sell_goods'),
                households.do('buy_goods'),
                households.do('consumption')

            simulation.graphs()

        if __name__ == '__main__':
            main(parameters)


Overview
~~~~~~~~

In start.py the simulation, thus the parameters, objects, agents and time line are
set up. Further it is declared, what is observed and written to the database.

.. code-block:: python

    from abce import Simulation, gui
    from firm import Firm
    from household import Household

Here the Agent class Firm is imported from the file firm.py. Likewise the Household class.
Further the Simulation base class and the graphical user interface (gui) are imported




Parameters are specified as a python dictionary

.. code-block:: python

    parameters = {'name': '2x2',
                  'random_seed': None,
                  'rounds': 10}


    @gui(simulation_parameters)
    def main(simulation_parameters):
        . . .

    if __name__ == '__main__':
        main(simulation_parameters)

The main function is generating and executing the simulation. When the main
function is preceded with :code:`@gui(simulation_parameters)` The graphical user interface is started
in your browser the simulation_parameters are used as default values. If no
browser window open you have to go manually to the
address "http://127.0.0.1:5000/". The graphical user interface starts the
simulation.

During development its often more practical run the simulation without
graphical user interface (GUI). In order to switch of the GUI comment
out the :code:`#@gui(simulation_parameters)`.
In order show graphs at the end of the simulation add :code:`simulation.graphs()`
after :code:`simulation.run`, as it is done in start.py above.


To set up a new model, you create a class instance a that will comprise your model

.. code-block:: python

    simulation = Simulation(rounds=simulation_parameters['rounds'], name="ABCE")

    ...

The order of actions: The order of actions within a round
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every agents-based model is characterized by the order of which the actions are executed.
In ABCE, there are rounds, every round is composed of sub-rounds, in which a group or
several groups of agents act in parallel. In the
code below you see a typical sub-round. Therefore after declaring the :code:`Simulation` the
order of actions, agents and objects are added.

.. code-block:: python

    for round in simulation.next_round():
        households.do('sell_labor')
        firms.do('buy_labor')
        firms.do('production')
        (households + firms).do('panel')
        firms.do('sell_goods')
        households.do('buy_goods')
        households.do('consumption')

This establishes the order of the simulation. Make sure you do not overwrite
internal abilities/properties of the agents. Such as 'sell', 'buy' or 'consume'.

A more complex example could be:

.. code-block:: python

    for round in simulation.next_round():
        if round % 30 == 0:
            households.do('sell_labor')
            firms.do('buy_labor')
        firms.do('production')
        (households + firms).do('panel')
        for i in range(10):
            firms.do('sell_goods')
            households.do('buy_goods')
        households.do('consumption')
        if round == 500:
            government.do('policy_change')

**Interactions happen between sub-rounds. An agent, sends a message in one round.
The receiving agent, receives the message the following sub-round.**  A trade is
finished in three rounds: (1) an agent sends an offer the good is blocked, so it
can not be sold twice (2) the other agent accepts or rejects it. (3) If
accepted, the good is automatically delivered at the beginning of the sub-round.
If the trade was rejected: the blocked good is automatically unblocked.

Special goods and services
~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we will establish properties of special goods. A normal good can just be
created or produced by an agent; it can also be destroyed, transformed or consumed
by an agent.
Some goods 'replenish' every round. And
some goods 'perish' every round. These properties have to be declared:


This example declares 'corn' perishable and every round the agent gets 100 units of
of 'corn' for every unit of field he possesses. If the corn is not consumed, it
automatically disappears at the end of the round.

.. code-block:: python

   simulation.declare_round_endowment('field', 100, 'corn')

   simulation.declare_round_endowment(resource='labor_endowment',
                                           units=1,
                                           product='labor'
        )

declare_round_endowment, establishes that at the beginning of every round,
every agent that possesses x units of a resource, gets x*units units of the product.
Every owner of x fields gets 100*x units of corn. Every owner of labor_endowment
gets one unit of labor for each unit of labor_endowment he owns. An agent has to
create the field or labor_endowment by :code:`self.create('field', 5)`, for
labor_endowment respectively.

.. code-block:: python

        simulation.declare_perishable('corn')
        simulation.declare_perishable(good='labor')


declare_perishable, establishes that every unit of the specified good that is not used by
the end of the round ceases to exist.

Declaring a good as replenishing and perishable is ABCE's way of treating services.
In this example every household has some units of labor that can be used in the
particular period. :py:meth:`abce.Simulation.declare_service` is a synthetic way
of declaring a good as a service.

One important remark, for a logically consistent **macro-model** it is best to
not create any goods during the simulation, but only in
:py:meth:`abce.Agent.init`. During the simulation the only new goods
should be created by :py:meth:`abce.Simulation.declare_round_endowment`.
In this way the economy is physically closed.

.. code-block:: python

        simulation.panel('household', possessions=['good1', 'good2'],  # a list of household possessions to track here
                                      variables=['utility']) #  a list of household variables to track here

        simulation.aggregate('household', possessions=['good1', 'good2'],
                              variables=['utility'])

The possessions good1 and good2 are tracked, the agent's variable :code:`self.utility` is tracked.
There are several ways in ABCE to log data. If you declare as above that the simulation
creates panel (:py:meth:`abce.Simulation.panel`) or aggregate (:py:meth:`abce.Simulation.aggregate`) data for the 'household', it creates and displays panel data of the evolution of variables and goods of the particular agent.


:py:meth:`abce.Simulation.panel` and :py:meth:`abec.Simulation.aggregate` only initialize the panel/aggregate data collection. You need to instruct
the Simulation, when to collect the data by adding 'panel' or 'aggregate' to the list of actions


.. code-block:: python

    (firms + households).do('panel')
    (firms + households).do'aggregate')


This will instruct the simulation that the firm and the household agent collect panel or aggregate data at a specific point in each round.


Alternative to this
you can also log within the agents by simply using `self.log('text', variable)` (:py:meth:`abce.Database.log`)

Having established special goods and logging, we create the agents:

.. code-block:: python

        simulation.build_agents(Firm, 'firm', number=simulation_parameters['number_of_firms'], parameters=simulation_parameters)
        simulation.build_agents(Household, 'household', number=10, parameters=simulation_parameters)

- Firm is the class of the agent, that you have imported
- 'firm' is the group_name of the agent
- number is the number of agents that are created
- parameters is a dictionary of parameters that the agent receives in the init function
  (which is discussed later)

.. code-block:: python

        simulation.build_agents(Plant, 'plant', parameters=simulation_parameters, agent_parameters=[{'type':'coal' 'watt': 20000},
                                                                                                    {'type':'electric' 'watt': 99}
                                                                                                    {'type':'water' 'watt': 100234}])

This builds three Plant agents. The first plant gets the first dictionary as a agent_parameter {'type':'coal' 'watt': 20000}.
The second agent, gets the second dictionary and so on.

The agents
----------

The Household agent
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from __future__ import division  # makes division work correctly
    import abce


    class Household(abce.Agent, abce.Household, abce.Trade):
        def init(self, simulation_parameters, agent_parameters):
            """ 1. labor_endowment, which produces, because of simulation.declare_resource(...)
            in start.py one unit of labor per month
            2. Sets the utility function to utility = consumption of good "GOOD"
            """
            self.create('labor_endowment', 1)
            self.set_cobb_douglas_utility_function({"GOOD": 1})
            self.current_utiliy = 0

        def sell_labor(self):
            """ offers one unit of labor to firm 0, for the price of 1 "money" """
            self.sell('firm', 0,
                      good="labor",
                      quantity=1,
                      price=1)

        def buy_goods(self):
            """ receives the offers and accepts them one by one """
            oo = self.get_offers("GOOD")
            for offer in oo:
                self.accept(offer)

        def consumption(self):
            """ consumes_everything and logs the aggregate utility. current_utiliy
            """
            self.current_utiliy = self.consume_everything()
            self.log_value('HH', self.current_utiliy)

The Firm agent
~~~~~~~~~~~~~~

.. code-block:: python

    from __future__ import division  # makes division work correctly
    import abce


    class Firm(abce.Agent, abce.Firm, abce.Trade):
        def init(self, simulation_parameters, agent_parameters):
            """ 1. Gets an initial amount of money
            2. create a cobb_douglas function: GOOD = 1 * labor ** 1.
            """
            self.create('money', 1)
            self.set_cobb_douglas("GOOD", 1, {"labor": 1})

        def buy_labor(self):
            """ receives all labor offers and accepts them one by one """
            oo = self.get_offers("labor")
            for offer in oo:
                self.accept(offer)

        def production(self):
            """ uses all labor that is available and produces
            according to the set cobb_douglas function """
            self.produce_use_everything()

        def sell_goods(self):
            """ offers one unit of labor to firm 0, for the price of 1 "money" """
            self.sell('household', 0,
                      good="GOOD",
                      quantity=self.possession("GOOD"),
                      price=1)


Agents are modeled in a separate file. In the template directory, you will find
two agents: :code:`firm.py` and :code:`household.py`.

At the beginning of each agent you will find

.. code-block:: python

    from __future__ import division

ABCE currently supports only python 2, which is still the most widely used python.
Python 2 has an odd way of handeling divisions this instructs python to handle division always as a
floating point division. Use this in all your python code. If you do not use this ``3 / 2 = 1``
instead of ``3 / 2 = 1.5`` (floor division).

An agent has to import the `abce` module and the :py:class:`abce.NotEnoughGoods` exception

.. code-block:: python

    import abce
    from abce import NotEnoughGoods

This imports the module abce in order to use the base classes Household and Firm.
And the NotEnoughGoods exception that allows us the handle situation in which the
agent has insufficient resources.

An agent is a class and must at least inherit :class:`abce.Agent`.
It automatically inherits :class:`abce.Trade` - :class:`abce.Messaging`
and :class:`abce.Database`

.. code-block:: python

    class Agent(abce.Agent):

To create an agent that has can create a consumption function and consume

.. code-block:: python

    class Household(abce.Agent, abce.Household):

To create an agent that can produce:

.. code-block:: python

    class Firm(abce.Agent, abce.Firm)

You see our Household agent inherits from :class:`abce.Agent`, which is compulsory and :class:`abce.Household`.
Household on the other hand are a set of methods that are unique for Household agents.
The Firm class accordingly

The init method
~~~~~~~~~~~~~~~

When an agent is created it's init function is called and the simulation
parameters as well as the agent_parameters are given to him

**DO NOT OVERWRITE THE __init__ method. Instead use ABCE's init method,
which is called when the agents are created**

.. code-block:: python

    def init(self, parameters, agent_parameters):
        self.create('labor_endowment', 1)
        self.set_cobb_douglas_utility_function({"MLK": 0.300, "BRD": 0.700})
        self.type = agent_parameters['type']
        self.watt = agent_parameters['watt']
        self.number_of_firms = parameters['number_of_firms']


The init method is the method that is called when the agents are created (by
the :py:meth:`abce.Simulation.build_agents`). When the agents were build,
a parameter dictionary and a list of agent parameters were given. These
can now be accessed in :code:`init`  via the :code:`parameters` and
:code:`agents_parameters` variable. Each agent gets only one element of the
:code:`agents_parameters` list.

With self.create the agent creates the good 'labor_endowment'. Any
good can be created. Generally speaking. In order to have a physically consistent
economy goods should only be created in the init method. The good money is used
in transactions.

This agent class inherited :py:meth:`abce.Household.set_cobb_douglas_utility_function`
from :class:`abce.Household`. With
:meth:`abce.Household.set_cobb_douglas_utility_function` you can create a
cobb-douglas function. Other functional forms are also available.

In order to let the agent remember a parameter it has to be saved in the self
domain of the agent.

The action methods and a consuming Household
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the other methods of the agent are executed when the corresponding sub-round is
called from the action_list in the Simulation in start.py.

For example when in the action list `('household', 'consumption')` is called the consumption method
is executed of each household agent is executed. **It is important not to
overwrite abce's methods with the agents method. For example if one would
call the :code:`consumption(self)` method below :code:`consume(self)`, abce's
consume function would not work anymore.

.. code-block:: python

    class Household(abce.Agent, abce.Household):
        def init(self, simulation_parameters, agent_parameters):
            self.create('labor_endowment', 1)
            self.set_cobb_douglas_utility_function({"GOOD": 1})
            self.current_utiliy = 0

        . . .

        def consumption(self):
            """ consumes_everything and logs the aggregate utility. current_utiliy
            """
            self.current_utiliy = self.consume_everything()
            self.log_value('HH', self.current_utiliy)



In the above example we see how a (degenerate) utility function is declared and how the
agent consumes. The dictionary assigns an exponent for each good, for example
a consumption function that has .5 for both exponents would be {'good1': 0.5, 'good2': 0.5}.

In the method `consumption`, which has to be called form the action_list in the
Simulation, everything is consumed an the utility from the consumption
is calculated and logged. The utility is logged and can be retrieved see
:doc:`retrieval of the simulation results`

Firms and Production functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Firms do two things they produce (transform) and trade. The following
code shows you how to declare a technology and produce bread from labor and
yeast.

.. code-block:: python

    class Agent(abce.Agent, abce.Firm):
        def init(self):
           set_cobb_douglas('bread', 1.890, {"yeast": 0.333, "labor": 0.667})
            ...

        def production(self):
            self.produce_use_everything()

More details in :class:`abce.Firm`. :class:`abce.FirmMultiTechnologies` offers
a more advanced interface for firms with layered production functions.

Trade
~~~~~

ABCE clears trade automatically. That means, that goods are automatically
exchanged, double selling of a good is avoided by subtracting a good from
the possessions when it is offered for sale. The modeler has only to decide
when the agent offers a trade and sets the criteria to accept the trade

.. code-block:: python

    # Agent 1
    def selling(self):
        offer = self.sell(buyer, 2, 'BRD', price=1, quantity=2.5)
        self.checkorders.append(offer)  # optional

    # Agent 2
    def buying(self):
        offers = self.get_offers('cookies')
        for offer in offers:
            if offer.price < 0.5
                try:
                    self.accept(offer)
                except NotEnoughGoods:
                    self.accept(offer, self.possession('money') / offer.price)

    # Agent 1
    def check_trade(self):
        print(self.checkorders[0])

Agent 1 sends a selling offer to Agent 2, which is the agent with the id :code:`2` from the :code:`buyer` group (:code:`buyer_2`)
Agent 2 receives all offers, he accepts all offers with a price smaller that 0.5. If
he has insufficient funds to accept an offer an NotEnoughGoods exception is thrown.
If a NotEnoughGoods exception is thrown the except block
:code:`self.accept(offer, self.possession('money') / offer.price)` is executed, which
leads to a partial accept. Only as many goods as the agent can afford are accepted.
If a polled offer is not accepted its automatically rejected. It can also be explicitly
rejected with :code:`self.reject(offer)` (:py:meth:`abce.Trade.reject`).

You can find a detailed explanation how trade works in :class:`abce.Trade`.

Data production
~~~~~~~~~~~~~~~

There are three different ways of observing your agents:

Trade Logging
+++++++++++++

when you specify :code:`Simulation(..., trade_logging='individual')`
all trades are recorded and a SAM or IO matrix is created.
This matrices are currently not display in the GUI, but
accessible as csv files in the :code:`simulation.path` directory

Manual in agent logging
+++++++++++++++++++++++

An agent can log a variable, :py:meth:`abce.Agent.possession`, :py:meth:`abce.Agent.possessions`
and most other methods such as :py:meth:`abce.Firm.produce` with :py:meth:`abce.Database.log`:

.. code-block:: python

    self.log('possessions', self.possessions())
    self.log('custom', {'price_setting': 5: 'production_value': 12})
    prod = self.production_use_everything()
    self.log('current_production', prod)


Retrieving the logged data
++++++++++++++++++++++++++

If the GUI is switched off there must be a
:py:meth:`abce.Simulation.graphs` afer :py:meth:`abce.Simulation.run` .
Otherwise no graphs are displayed.
If no browser window open you have to go manually to the
address "http://127.0.0.1:5000/"

The results are stored in a subfolder of the ./results/ folder.
:code:`simulation.path` gives you the path to that folder.

The tables are stored as '.csv' files which can be opened with excel.



Have a look on the `abce/examples/` folder
------------------------------------------

It is instructive to look at a more examples, for example the 2x2 economy '2sectors'.
All examples can be found in the abce/example folder, wich you can
download from https://github.com/DavoudTaghawiNejad/abce/archive/master.zip at
https://github.com/DavoudTaghawiNejad/abce

Then you can make a working copy of the template or a copy of an example.

In the remainder of this walkthrough we will discus a minimal agent based model in ABCE


.. [#remainder] round % 2 == 0 means the remainder of round divided by 2 is zero.
