Walk through
============

In order to learn using abcEconomics we will now dissect and explain a simple abcEconomics model.
Additional to this walk through you should also have a look on the examples in
 <https://github.com/AB-CE/examples>(https://github.com/AB-CE/examples),


.. sidebar:: Objects the other ontological object of agent-based models.

 Objects have a special stance in agent-based modeling:
    -  objects can be recovered (resources)
    -  exchanged (trade)
    -  transformed (production)
    -  consumed
    -  destroyed (not really) and time depreciated

    abcEconomics, takes care of trade, production / transformation and consumption
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

        """ 1. Build a Simulation
            2. Build one Household and one Firm follow_agent
            3. For every labor_endowment an agent has he gets one trade or usable labor
            per round. If it is not used at the end of the round it disappears.
            4. Firms' and Households' possessions are monitored to the points marked in
            timeline.
        """

        from abcEconomics import Simulation, gui
        from firm import Firm
        from household import Household


        def main():
            simulation = Simulation()

            firms = simulation.build_agents(Firm, 'firm', 1)
            households = simulation.build_agents(Household, 'household', 1)

            for r in range(100):
                simulation.advance_round(r)
                households.sell_labor()
                firms.buy_labor()
                firms.production()
                (households + firms).panel_log(possessions=['money', 'GOOD'])
                households.panel_log(variables=['current_utility'])
                firms.sell_goods()
                households.buy_goods()
                households.consumption()
                (households + firms).refresh_services(service='labor' , derived_from='labor_endowment', units=1)

            simulation.graphs()

        if __name__ == '__main__':
            main()

It is of utter most importance to end with either simulation.graphs() or simulation.finalize()

A simulation with GUI
~~~~~~~~~~~~~~~~~~~~~

In start.py the simulation, thus the parameters, objects, agents and time line are
set up. Further it is declared, what is observed and written to the database.

.. code-block:: python

    from abcEconomics import Simulation, gui
    from firm import Firm
    from household import Household

Here the Agent class Firm is imported from the file firm.py. Likewise the Household class.
Further the Simulation base class and the graphical user interface (gui) are imported




Parameters are specified as a python dictionary

.. code-block:: python

    parameters = {'name': '2x2',
                  'random_seed': None,
                  'rounds': 10,
                  'slider': 100.0,
                  'Checkbox': True,
                  'Textbox': 'type here',
                  'integer_slider': 100,
                  'limited_slider': (20, 25, 50)}


    @gui(parameters)
    def main(parameters):
        . . .

    if __name__ == '__main__':
        main(parameters)

The main function is generating and executing the simulation. When the main
function is preceded with :code:`@gui(simulation_parameters)` The graphical user interface is started
in your browser the simulation_parameters are used as default values. If no
browser window open you have to go manually to the
address "http://127.0.0.1:8000/". The graphical user interface starts the
simulation.

During development its often more practical run the simulation without
graphical user interface (GUI). In order to switch of the GUI comment
out the :code:`#@gui(simulation_parameters)`.
In order show graphs at the end of the simulation add :code:`simulation.graphs()`
after :code:`simulation.run`, as it is done in start.py above.


To set up a new model, you create a class instance a that will comprise your model

.. code-block:: python

    simulation = Simulation(name="abcEconomics")

    ...

The order of actions: The order of actions within a round
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every agents-based model is characterized by the order of which the actions are executed.
In abcEconomics, there are rounds, every round is composed of sub-rounds, in which a group or
several groups of agents act in parallel. In the
code below you see a typical sub-round. Therefore after declaring the :code:`Simulation` the
order of actions, agents and objects are added.

.. code-block:: python

    for round in range(1000):
        simulation.advance_round(round)
        households.sell_labor()
        firms.buy_labor()
        firms.production()
        (households + firms).panel_log(...)
        firms.sell_goods()
        households.buy_goods()
        households.consumption()

This establishes the order of the simulation. Make sure you do not overwrite
internal abilities/properties of the agents. Such as 'sell', 'buy' or 'consume'.

A more complex example could be:

.. code-block:: python

    for week in range(52):
        for day in ['mo', 'tu', 'we', 'th', 'fr']:
        simulation.advance_round((week, day))
        if day = 'mo':
            households.sell_labor()
            firms.buy_labor()
        firms.production()
        (households + firms).panel()
        for i in range(10):
            firms.sell_goods()
            households.buy_goods()
        households.consumption()
        if week == 26:
            government.policy_change()

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
some goods 'perish' every round. These properties have to be refreshed at the
end of every round:

.. code-block:: python

    for round in range(1000):
        simulation.advance_round(round)
        # ...
        (households + firms).refresh_services(service='labor' , derived_from='labor_endowment', units=1)

In this example, the refresh_services removes the existing 'labor' goods and
regenerates 1 unit of labor from scratch from every unit of labor_endowment

One important remark, for a logically consistent **macro-model** it is best to
not create any goods during the simulation, but only in
:py:meth:`abcEconomics.Agent.init`. During the simulation the only new goods
should be created by :py:meth:`abcEconomics.Goods.refresh_services`.
In this way the economy is physically closed.

.. code-block:: python

        firms.panel_log(possessions=['good1', 'good2') # a list of firm possessions to track here

        households.agg_log('household', possessions=['good1', 'good2'],
                            variables=['utility']) #  a list of household variables to track here

The possessions good1 and good2 are tracked, the agent's variable :code:`self.utility` is tracked.
There are several ways in abcEconomics to log data. Note that the variable names a strings.




Alternative to this
you can also log within the agents by simply using `self.log('text', variable)` (:py:meth:`abcEconomics.Database.log`)
Or self.log('text', {'var1': var1, 'var2': var2}). Using one log command with a dictionary is faster than
using several seperate log commands.

Having established special goods and logging, we create the agents:

.. code-block:: python

        simulation.build_agents(Firm, 'firm', number=simulation_parameters['number_of_firms'], parameters=simulation_parameters)
        simulation.build_agents(Household, 'household', number=10, parameters=simulation_parameters)

- Firm is the class of the agent, that you have imported
- 'firm' is the group_name of the agent
- number is the number of agents that are created
- parameters is a dictionary of parameters that the agent receives in the :code:`init` function
  (which is discussed later)

.. code-block:: python

        simulation.build_agents(Plant, 'plant',
                                parameters=simulation_parameters,
                                agent_parameters=[{'type':'coal' 'watt': 20000},
                                                  {'type':'electric' 'watt': 99}
                                                  {'type':'water' 'watt': 100234}])

This builds three Plant agents. The first plant gets the first dictionary as a agent_parameter {'type':'coal' 'watt': 20000}.
The second agent, gets the second dictionary and so on.

The agents
----------

The Household agent
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import abcEconomics


    class Household(abcEconomics.Agent, abcEconomics.Household, abcEconomics.Trade):
        def init(self, simulation_parameters, agent_parameters):
            """ 1. labor_endowment, which produces, because of simulation.declare_resource(...)
            in start.py one unit of labor per month
            2. Sets the utility function to utility = consumption of good "GOOD"
            """
            self.create('labor_endowment', 1)
            self.set_cobb_douglas_utility_function({"GOOD": 1})
            self.current_utility = 0

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
            """ consumes_everything and logs the aggregate utility. current_utility
            """
            self.current_utility = self.consume_everything()
            self.log('HH', self.current_utility)

The Firm agent
~~~~~~~~~~~~~~

.. code-block:: python

    import abcEconomics


    class Firm(abcEconomics.Agent, abcEconomics.Firm, abcEconomics.Trade):
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

An agent has to import the `abcEconomics` module and the :py:class:`abcEconomics.NotEnoughGoods` exception

.. code-block:: python

    import abcEconomics
    from abcEconomics import NotEnoughGoods

This imports the module abcEconomics in order to use the base classes Household and Firm.
And the NotEnoughGoods exception that allows us the handle situation in which the
agent has insufficient resources.

An agent is a class and must at least inherit :class:`abcEconomics.Agent`.
It automatically inherits :class:`abcEconomics.Trade` - :class:`abcEconomics.Messenger`
and :class:`abcEconomics.Logger`

.. code-block:: python

    class Agent(abcEconomics.Agent):

To create an agent that has can create a consumption function and consume

.. code-block:: python

    class Household(abcEconomics.Agent, abcEconomics.Household):

To create an agent that can produce:

.. code-block:: python

    class Firm(abcEconomics.Agent, abcEconomics.Firm)

You see our Household agent inherits from :class:`abcEconomics.Agent`, which is compulsory and :class:`abcEconomics.Household`.
Household on the other hand are a set of methods that are unique for Household agents.
The Firm class accordingly

The init method
~~~~~~~~~~~~~~~

When an agent is created it's init function is called and the simulation
parameters as well as the agent_parameters are given to him

**DO NOT OVERWRITE THE __init__ method. Instead use abcEconomics's init method,
which is called when the agents are created**

.. code-block:: python

    def init(self, parameters, agent_parameters):
        self.create('labor_endowment', 1)
        self.set_cobb_douglas_utility_function({"MLK": 0.300, "BRD": 0.700})
        self.type = agent_parameters['type']
        self.watt = agent_parameters['watt']
        self.number_of_firms = parameters['number_of_firms']


The init method is the method that is called when the agents are created (by
the :py:meth:`abcEconomics.Simulation.build_agents`). When the agents were build,
a parameter dictionary and a list of agent parameters were given. These
can now be accessed in :code:`init`  via the :code:`parameters` and
:code:`agents_parameters` variable. Each agent gets only one element of the
:code:`agents_parameters` list.

With self.create the agent creates the good 'labor_endowment'. Any
good can be created. Generally speaking. In order to have a physically consistent
economy goods should only be created in the init method. The good money is used
in transactions.

This agent class inherited :py:meth:`abcEconomics.Household.set_cobb_douglas_utility_function`
from :class:`abcEconomics.Household`. With
:meth:`abcEconomics.Household.set_cobb_douglas_utility_function` you can create a
cobb-douglas function. Other functional forms are also available.

In order to let the agent remember a parameter it has to be saved in the self
domain of the agent.

The action methods and a consuming Household
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the other methods of the agent are executed when the corresponding sub-round is
called from the action_list in the Simulation in start.py.

For example when in the action list `('household', 'consumption')` is called the consumption method
is executed of each household agent is executed. **It is important not to
overwrite abcEconomics's methods with the agents methods.** For example if one would
call the :code:`consumption(self)` method below :code:`consume(self)`, abcEconomics's
consume function would not work anymore.

.. code-block:: python

    class Household(abcEconomics.Agent, abcEconomics.Household):
        def init(self, simulation_parameters, agent_parameters):
            self.create('labor_endowment', 1)
            self.set_cobb_douglas_utility_function({"GOOD": 1})
            self.current_utility = 0

        . . .

        def consumption(self):
            """ consumes_everything and logs the aggregate utility. current_utility
            """
            self.current_utility = self.consume_everything()
            self.log('HH', self.current_utility)



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

    class Agent(abcEconomics.Agent, abcEconomics.Firm):
        def init(self):
           set_cobb_douglas('bread', 1.890, {"yeast": 0.333, "labor": 0.667})
            ...

        def production(self):
            self.produce_use_everything()

More details in :class:`abcEconomics.Firm`. :class:`abcEconomics.FirmMultiTechnologies` offers
a more advanced interface for firms with layered production functions.

Trade
~~~~~

abcEconomics clears trade automatically. That means, that goods are automatically
exchanged, double selling of a good is avoided by subtracting a good from
the possessions when it is offered for sale. The modeler has only to decide
when the agent offers a trade and sets the criteria to accept the trade

.. code-block:: python

    # Agent 1
    def selling(self):
        offer = self.sell(buyer, 2, 'BRD', price=1, quantity=2.5)
        self.checkorders.append(offer)  # optional


.. code-block:: python


    # Agent 2
    def buying(self):
        offers = self.get_offers('cookies')
        for offer in offers:
            if offer.price < 0.5
                try:
                    self.accept(offer)
                except NotEnoughGoods:
                    self.accept(offer, self.possession('money') / offer.price)


.. code-block:: python

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
rejected with :code:`self.reject(offer)` (:py:meth:`abcEconomics.Trade.reject`).

You can find a detailed explanation how trade works in :class:`abcEconomics.Trade`.

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

An agent can log a variable, :py:meth:`abcEconomics.Agent.possession`, :py:meth:`abcEconomics.Agent.possessions`
and most other methods such as :py:meth:`abcEconomics.Firm.produce` with :py:meth:`abcEconomics.Database.log`:

.. code-block:: python

    self.log('possessions', self.possessions())
    self.log('custom', {'price_setting': 5: 'production_value': 12})
    prod = self.production_use_everything()
    self.log('current_production', prod)


Retrieving the logged data
++++++++++++++++++++++++++

If the GUI is switched off there must be a
:py:meth:`abcEconomics.Simulation.graphs` after :py:meth:`abcEconomics.Simulation.run` .
Otherwise no graphs are displayed.
If no browser window open you have to go manually to the
address "http://127.0.0.1:8000/"

The results are stored in a subfolder of the ./results/ folder.
:code:`simulation.path` gives you the path to that folder.

The tables are stored as '.csv' files which can be opened with excel.

.. [#remainder] round % 2 == 0 means the remainder of round divided by 2 is zero.
