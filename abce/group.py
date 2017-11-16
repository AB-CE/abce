""" Copyright 2012 Davoud Taghawi-Nejad

 Module Author: Davoud Taghawi-Nejad

 ABCE is open-source software. If you are using ABCE for your research you are
 requested the quote the use of this software.

 Licensed under the Apache License, Version 2.0 (the "License"); you may not
 use this file except in compliance with the License and quotation of the
 author. You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 License for the specific language governing permissions and limitations under
 the License.
"""
# pylint: disable=W0212, C0111
from collections import deque, defaultdict


def _get_methods(agent_class):
    """ Returns all public methods of a class as a set, except for init """
    return set(method
               for method in dir(agent_class)
               if callable(getattr(agent_class, method)) and
               method[0] != '_' and method != 'init')


class Group(object):
    """ A group of agents. Groups of agents inherit the actions of the agents class they are created by.
    When a group is called with an agent action all agents execute this actions simultaneously.
    e.G. :code:`banks.buy_stocks()`, then all banks buy stocks simultaneously.

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

    future:

    agents actions can also be combined::

        buying_stuff = banks.buy_stocks + hedgefunds.buy_feraries
        buy_stocks()

    or::


        (banks.buy_stocks & hedgefunds.buy_feraries)()



    """
    def __init__(self, sim, processorgroup, group_names, agent_classes, ids=None, agent_arguments=None):
        self.sim = sim
        self.num_managers = sim.processes
        self._agents = processorgroup
        self.group_names = group_names
        self.agent_classes = agent_classes
        self._agent_arguments = agent_arguments
        for method in set.intersection(*(_get_methods(agent_class) for agent_class in agent_classes)):
            setattr(self, method,
                    eval('lambda self=self, *argc, **kw: self.do("%s", *argc, **kw)' %
                         method))

        self.panel_serial = 0
        self.last_action = "Begin_of_Simulation"

        if len(group_names) == 1:
            self.free_ids = defaultdict(deque)
            if group_names[0] not in self._agents.group_names():
                self._agents.new_group(group_names[0])
        if ids is None:
            self._ids = [[]]
        else:
            self._ids = ids

    def __add__(self, other):
        return Group(self.sim, self._agents, self.group_names + other.group_names, self.agent_classes + other.agent_classes, self._ids + other._ids)

    def __radd__(self, g):
        if isinstance(g, Group):
            return self.__add__(g)
        else:
            return self

    def panel_log(self, variables=[], possessions=[], func={}, len=[]):
        """ panel_log(.) writes a panel of variables and possessions
        of a group of agents into the database, so that it is displayed
        in the gui.

        Args:
            possessions (list, optional):
                a list of all possessions you want to track as 'strings'
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
                firms.panel_log(possessions=['money', 'input'],
                            variables=['production_target', 'gross_revenue'])
                households.buying()
        """
        self.do('_panel_log', variables, possessions, func, len, self.last_action)

    def agg_log(self, variables=[], possessions=[], func={}, len=[]):
        """ agg_log(.) writes a aggregate data of variables and possessions
        of a group of agents into the database, so that it is displayed
        in the gui.

        Args:
            possessions (list, optional):
                a list of all possessions you want to track as 'strings'
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
                firms.agg_log(possessions=['money', 'input'],
                            variables=['production_target', 'gross_revenue'])
                households.buying()
        """
        self.do('_agg_log', variables, possessions, func, len)

    def create_agents(self, simulation_parameters=None, agent_parameters=None, number=1):
        """ Create a new agent to this group. Works only for non-combined groups

        Args:
            number:
                number of agents to create if agent_parameters is not set

            simulation_parameters:
                A dictionary of simulation_parameters

            agent_parameters:
                List of dictionaries of agent_parameters

        Returns:
            The id of the new agent
        """
        if agent_parameters is None:
            agent_parameters = [[]] * number
        assert len(self.group_names) == 1, 'Group is a combined group, no appending permitted'
        group_name = self.group_names[0]
        ids = []
        for _ in range(len(agent_parameters)):
            if self.free_ids[group_name]:
                id = self.free_ids[group_name].popleft()
                self._ids[0][id] = id
            else:
                id = len(self._ids[0])
                self._ids[0].append(id)
            ids.append(id)

        Agent = self.agent_classes[0]

        self._agents.insert_or_append(group_name, ids, Agent, simulation_parameters, agent_parameters, self._agent_arguments)
        return ids

    def do(self, command, *args, **kwargs):
        """ agent actions can be executed by group.action() or group.do('action') """
        self.last_action = command
        return self._agents.do(self.group_names, self._ids, command, args, kwargs)

    def delete_agents(self, ids):
        """ Remove an agent from not combined group, by specifying his ID:

        Args:
            id:
                id of the agent
        """
        assert len(self.group_names) == 1, 'Group is a combined group, no deleting permitted'
        for id in ids:
            assert self._ids[0][id] == id
            self._ids[0][id] = None
        self._agents.delete_agents(self.group_names[0], ids)
        self.free_ids[self.group_names[0]].extend(ids)

    def __getitem__(self, *ids):
        if isinstance(*ids, int):
            ids = [ids]
        return Group(self.sim, self._agents, self.group_names, self.agent_classes, ids=ids * len(self.group_names))

    def __len__(self):
        """ Returns the length of a group """
        return sum([len(groupids) for groupids in self._ids])

    def __repr__(self):
        return repr(self)
