# Copyright 2012 Davoud Taghawi-Nejad
#
#  Module Author: Davoud Taghawi-Nejad
#
#  abcEconomics is open-source software. If you are using abcEconomics for your research you are
#  requested the quote the use of this software.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not
#  use this file except in compliance with the License and quotation of the
#  author. You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations under
# the License.


class Chain:
    def __init__(self, iterables):
        self.iterables = iterables

    def __iter__(self):
        for it in self.iterables:
            for element in it:
                yield element

    def __repr__(self):
        return repr(list(self.iterables))

    def __str__(self):
        return str(list(self.iterables))

    def __getitem__(self, item):
        try:
            return self.iterables[item]
        except IndexError:
            self.iterables = [i for i in iter(self)]
            return self.iterables[item]


class Action:
    # This allows actions of Group to be combined. For example::
    #
    #     (firms.sell & households.buy)()
    #
    # It works by returning a callable and combinable action from
    # the groups __getattr__ method.

    def __init__(self, scheduler, actions):
        self._scheduler = scheduler
        self.actions = actions

    def __add__(self, other):
        return Action(self._scheduler, self.actions + other.actions)

    def __call__(self, *args, **kwargs):
        for names, command, _, __ in self.actions:
            self._scheduler.do(names, command, args, kwargs)
        return Chain([self._scheduler.post_messages(action[0]) for action in self.actions])
        # itertools.chain, does not work here


class Group:
    """ A group of agents. Groups of agents inherit the actions of the agents class they are created by.
    When a group is called with an agent action all agents execute this actions simultaneously.
    e.G. :code:`banks.buy_stocks()`, then all banks buy stocks simultaneously.

    agents groups are created like this::

        sim = Simulation()

        Agents = sim.build_agents(AgentClass, 'group_name', number=100, param1=param1, param2=param2)
        Agents = sim.build_agents(AgentClass, 'group_name',
                                  param1=param1, param2=param2,
                                  agent_parameters=[dict(ap=ap1_agentA, ap=ap2_agentA),
                                                    dict(ap=ap1_agentB, ap=ap2_agentB),
                                                    dict(ap=ap1_agentC, ap=ap2_agentC)])

    Agent groups can be combined using the + sign::

        financial_institutions = banks + hedgefunds
        ...
        financial_institutions.buy_stocks()

    or::

       (banks + hedgefunds).buy_stocks()

    Simultaneous execution means that all agents act on the same information set and influence each other
    only after this action.

    individual agents in a group are addressable, you can also get subgroups (only from non combined groups):

        banks[5].buy_stocks()

        (banks[6,4] + hedgefunds[7,9]).buy_stocks()


    agents actions can also be combined::

        buying_stuff = banks.buy_stocks & hedgefunds.buy_feraries
        buy_stocks()

    or::


        (banks.buy_stocks & hedgefunds.buy_feraries)()

    """

    def __init__(self, sim, scheduler, names, agent_arguments=None):
        self.sim = sim
        self.num_managers = sim.processes
        self._scheduler = scheduler
        if names is None:
            self.names = set()
        else:
            self.names = names
        self._agent_arguments = agent_arguments
        self.panel_serial = 0
        self.last_action = "Begin_of_Simulation"
        self.num_agents = 0
        if agent_arguments is not None:
            self.agent_name_prefix = agent_arguments['group']

    def __add__(self, other):
        return Group(self.sim, self._scheduler, self.names.union(other.names))

    def __radd__(self, g):
        if isinstance(g, Group):
            return self.__add__(g)
        else:
            return self

    def panel_log(self, variables=[], goods=[], func={}, len=[]):
        """ panel_log(.) writes a panel of variables and goods
        of a group of agents into the database, so that it is displayed
        in the gui.

        Args:
            goods (list, optional):
                a list of all goods you want to track as 'strings'
            variables (list, optional):
                a list of all variables you want to track as 'strings'
            func (dict, optional):
                accepts lambda functions that execute functions. e.G.
                :code:`func = lambda self: self.old_money - self.new_money`
            len (list, optional):
                records the length of the list or dictionary with that name.

        Example in start.py::

            for round in simulation.next_round():
                firms.produce_and_sell()
                firms.panel_log(goods=['money', 'input'],
                            variables=['production_target', 'gross_revenue'])
                households.buying()
        """
        self._do('_panel_log', variables, goods, func, len, self.last_action)

    def agg_log(self, variables=[], goods=[], func={}, len=[]):
        """ agg_log(.) writes a aggregate data of variables and goods
        of a group of agents into the database, so that it is displayed
        in the gui.

        Args:
            goods (list, optional):
                a list of all goods you want to track as 'strings'
            variables (list, optional):
                a list of all variables you want to track as 'strings'
            func (dict, optional):
                accepts lambda functions that execute functions. e.G.
                :code:`func = lambda self: self.old_money - self.new_money`
            len (list, optional):
                records the length of the list or dictionary with that name.

        Example in start.py::

            for round in simulation.next_round():
                firms.produce_and_sell()
                firms.agg_log(goods=['money', 'input'],
                            variables=['production_target', 'gross_revenue'])
                households.buying()
        """
        self._do('_agg_log', variables, goods, func, len)

    def create_agents(self, Agent, number=1, agent_parameters=None, **common_parameters):
        """ Create new agents to this group. Works only for non-combined groups

        Args:
            Agent:
                The class used to initialize the agents
            agent_parameters:
                List of dictionaries of agent_parameters

            number:
                number of agents to create if agent_parameters is not set

            any keyword parameter:
                parameters directly passed to :code:`agent.init` methood

        Returns:
            The id of the new agent
        """
        if agent_parameters is None:
            agent_parameters = number

        new_names = self._scheduler.add_agents(Agent, common_parameters, agent_parameters, self._agent_arguments, self.num_agents)
        self.num_agents += len(new_names)
        self.names.update(new_names)
        return new_names

    def _do(self, command, *args, **kwargs):
        """ agent actions can be executed by :code:`group.action(args=args)`. """
        self.last_action = command
        return self._scheduler.do(self.names, command, args, kwargs)

    def __getattr__(self, command, *args, **kwargs):
        self.last_action = command
        return Action(self._scheduler, [(self.names, command, args, kwargs)])

    def delete_agents(self, names):
        """ Remove an agents from a group, by specifying their id.

        Args:
            ids:
                list of ids of the agent

        Example::

            students.delete_agents([1, 5, 15])
        """
        for name in names:
            self.names.remove(name)
        self._scheduler.delete_agents(names)

    def __getitem__(self, ids):
        try:
            names = {(self.agent_name_prefix, id) for id in ids}
        except TypeError:
            names = {(self.agent_name_prefix, ids)}
        return Group(self.sim, self._scheduler, names, self._agent_arguments)

    def by_names(self, names):
        """ Return a callable group of agents from a list of names.group

        Example::

            banks.by_names(['UBS', 'RBS', "DKB"]).give_loans() """
        names = set(names)
        return Group(self.sim, self._scheduler, names, self._agent_arguments)

    def by_name(self, name):
        """ Return a group of a single agents by its name """
        names = {name}
        return Group(self.sim, self._scheduler, names, self._agent_arguments)

    def __len__(self):
        """ Returns the length of a group """
        return len(self.names)

    def __repr__(self):
        return repr(self.names)
