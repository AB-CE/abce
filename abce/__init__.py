# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# pylint: disable=W0212, C0111


""" The best way to start creating a simulation is by copying the start.py
file and other files from 'abce/template' in https://github.com/AB-CE/examples.

To see how to create a simulation, read :doc:`ipython_tutorial`.


This is a minimal template for a start.py::

    from agent import Agent
    from abce import *


    simulation = Simulation(name='ABCE')
    agents = simulation.build_agents(Agent, 'agent', 2)
    for time in range(100):
        simulation.advance_round(time)
        agents.one()
        agents.two()
        agents.three()
    simulation.graphs()

Note two things are important: there must be either a

:func:`~abce.simulation.graphs` or a :func:`~abce.simulation.finalize` at the end
otherwise the simulation blocks at the end.
Furthermore, every round needs to be announced using simulation.advance_round(time),
where time is any representation of time.

"""
import datetime
import os
import time
import random
import json
import queue
import multiprocessing as mp
from collections import OrderedDict
from .db import Database
from .agent import Agent, Trade  # noqa: F401
from .group import Group
from .notenoughgoods import NotEnoughGoods  # noqa: F401
from .agents import Firm, Household  # noqa: F401
from .quote import Quote  # noqa: F401
from .contracts import Contracting  # noqa: F401
from .gui import gui, graphs  # noqa: F401
from .singleprocess import SingleProcess
from .multiprocess import MultiProcess


class Simulation(object):
    """ This is the class in which the simulation is run. Actions and agents have to
    be added. Databases and resource declarations can be added. Then run
    the simulation.

    Args:
        name:
            name of the simulation

        random_seed (optional):
            a random seed that controls the random number of the simulation

        trade_logging:
            Whether trades are logged,trade_logging can be
            'group' (fast) or 'individual' (slow) or 'off'

        processes (optional):
            The number of processes that runs in parallel. Each process hosts
            a share of the agents.
            By default, if this parameter is not specified, `processes` is all
            your logical processor cores times two, using hyper-threading when available.
            For easy debugging, set processes to one and the simulation is
            executed without parallelization.
            Sometimes it is advisable to decrease the number of processes to
            the number of logical or even physical processor cores on your
            computer.
            **For easy debugging set processes to 1, this way only one agent
            runs at a time and only one error message is displayed**

        check_unchecked_msgs:
            check every round that all messages have been received with get_massages or get_offers.

        Example::

            simulation = Simulation(name='ABCE',
                                    trade_logging='individual',
                                    processes=None)


    Example for a simulation::

        num_firms = 5
        num_households = 2000

        w = Simulation(name='ABCE',
                       trade_logging='individual',
                       processes=None)

        w.declare_round_endowment(resource='labor_endowment',
                                  productivity=1,
                                  product='labor')

        w.panel('firm', command='after_sales_before_consumption')

        firms = w.build_agents(Firm, 'firm', num_firms)
        households = w.build_agents(Household, 'household', num_households)

        all = firms + households

        for r in range(100):
            self.advance_round(r)
            households.recieve_connections()
            households.offer_capital()
            firms.buy_capital()
            firms.production()
            if r == 250:
                centralbank.intervention()
            households.buy_product()
            all.after_sales_before_consumption()
            households.consume()

        w.finalize()
        w.graphs()
    """

    def __init__(self, name='abce', random_seed=None,
                 trade_logging='off', processes=1, check_unchecked_msgs=False):
        """
        """
        try:
            name = simulation_name  # noqa: F821
        except NameError:
            pass

        self.check_unchecked_msgs = check_unchecked_msgs

        self.agents_created = False
        self._messages = {}
        self._resource_command_group = {}
        self._db_commands = {}
        self.num_agents = 0
        self._build_first_run = True
        self.resource_endowment = []
        self.perishable = []
        self.expiring = []

        os.makedirs(os.path.abspath('.') + '/result/', exist_ok=True)

        self.path = (os.path.abspath('.') + '/result/' + name + '_' +
                     datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
        """ the path variable contains the path to the simulation outcomes
        it can be used to generate your own graphs as all resulting
        csv files are there.
        """
        while True:
            try:
                os.makedirs(self.path)
                break
            except OSError:
                self.path += 'I'

        self.trade_logging_mode = trade_logging
        if self.trade_logging_mode not in ['individual', 'group', 'off']:
            Exception("trade_logging can be "
                      "'group' (fast) or 'individual' (slow) or 'off'"
                      ">" + self.trade_logging_mode + "< not accepted")

        self.processes = mp.cpu_count() * 2 if processes is None else processes

        if processes == 1:
            self._processorgroup = SingleProcess()
            self.database_queue = queue.Queue()
        else:
            self._processorgroup = MultiProcess(processes)
            manager = mp.Manager()
            self.database_queue = manager.Queue()

        self.messagess = {}

        self._db = Database(
            self.path,
            self.database_queue,
            trade_log=self.trade_logging_mode != 'off')
        self._db_started = False

        if random_seed is None or random_seed == 0:
            random_seed = time.time()
        random.seed(random_seed)

        self.sim_parameters = OrderedDict(
            {'name': name, 'random_seed': random_seed})
        self.clock = time.time()
        self.database = self
        self.time = None
        """Returns the current time set with simulation.advance_round(time)"""
        self._groups = {}

    def declare_round_endowment(self, resource, units,
                                product):
        """ At the beginning of very round the agent gets 'units' units
        of good 'product' for every 'resource' he possesses.

        Round endowments are group specific, that means when
        somebody except the specified group holds them they do not produce.

        Args::

            resource:
                The good that you have to hold to get the other

            units:
                the multiplier to get the produced good

            product:
                the good that is produced if you hold the first good

            groups:
                a list of agent groups, which gain the second good,
                if they hold the first one

        Example::

            A farmer gets a ton of harvest for every acre:

            w.declare_round_endowment(resource='land',
                                      units=1000,
                                      product='wheat')
        """
        if self.agents_created:
            raise Exception(
                "WARNING: declare_round_endowment(...)"
                " must be called before the agents are build")
        self.resource_endowment.append(
            (resource, units, product))

    def declare_perishable(self, good):
        """ This good only lasts one round and then disappears. For example
        labor, if the labor is not used today today's labor is lost.
        In combination with resource this is useful to model labor or capital.

        In the example below a worker has an endowment of labor and capital.
        Every round he can sell his labor service and rent his capital. If
        he does not the labor service for this round and the rent is lost.

        Args::

         good:
            the good that perishes

         Example::

             w.declare_perishable(good='LAB')
             w.declare_perishable(good='CAP')

        """
        if self.agents_created:
            raise Exception(
                "WARNING: declare_perishable(...) must be called before "
                "the agents are build")
        self.perishable.append(good)

    def declare_expiring(self, good, duration):
        """ This type of good lasts for several rounds, but eventually
        expires. For example computers would last for several years and than
        become obsolete.

        Args:

            good:
                the good, which expires
            duration:
                the duration before the good expires
        """
        if self.agents_created:
            raise Exception(
                "WARNING: declare_expiring(...) must be called "
                "before the agents are build")
        self.expiring.append((good, duration))

    def declare_service(self, human_or_other_resource,
                        units, service):
        """ When the agent holds the human_or_other_resource,
        he gets 'units' of service every round
        the service can be used only with in this round.

        Args::

            human_or_other_resource:
                the good that needs to be in possessions to create the other
                good 'self.create('adult', 2)'
            units:
                how many units of the service is available
            service:
                the service that is created
            groups:
                a list of agent groups that can create the service

        Example::

            For example if a household has two adult family members, it gets
            16 hours of work

            w.declare_service('adult', 8, 'work')
        """
        self.declare_round_endowment(
            human_or_other_resource, units, service)
        self.declare_perishable(service)

    def advance_round(self, time):
        if not self._db_started:
            self._db.start()
            self._db_started = True
        self.time = time
        print("\rRound" + str(time))
        self._processorgroup.advance_round(time)

    def __del__(self):
        self.finalize()

    def finalize(self):
        """ simulation.finalize() must be run after each simulation. It will
        write all data to disk

        Example::

            simulation = Simulation(...)
            ...
            for r in range(100):
                simulation.advance_round(r)
                agents.do_something()
                ...

            simulation.finalize()
        """
        if self._db_started:
            self._db_started = False
            print('')
            print(str("time only simulation %6.2f" %
                  (time.time() - self.clock)))

            self.database_queue.put('close')

            while self._db.is_alive():
                time.sleep(0.05)

            try:
                self.pool.close()
                self.pool.join()
            except AttributeError:
                pass

            print(str("time with data %6.2f" %
                      (time.time() - self.clock)))
            self._write_description_file()
            self._displaydescribtion()

    def build_agents(self, AgentClass, group_name,
                     number=None,
                     agent_parameters=None,
                     **parameters):
        """ This method creates agents.

        Args:

            AgentClass:
                is the name of the AgentClass that you imported

            group_name:
                the name of the group, as it will be used in the action list
                and transactions. Should generally be lowercase of the
                AgentClass.

            number:
                number of agents to be created.

            agent_parameters:
                a list of dictionaries, where each agent gets one dictionary.
                The number of agents is the length of the list

            any other parameters:
                are directly passed to the agent

        Example::

         firms = simulation.build_agents(Firm, 'firm',
             number=simulation_parameters['num_firms'])
         banks = simulation.build_agents(Bank, 'bank',
                                         agent_parameters=[{'name': 'UBS'},
                                         {'name': 'amex'},{'name': 'chase'}
                                         **simulation_parameters,
                                         loanable=True)

         centralbanks = simulation.build_agents(CentralBank, 'centralbank',
                                                number=1,
                                                rounds=num_rounds)
        """
        assert number is None or agent_parameters is None, \
            'either set number or agent_parameters in build_agents'
        assert group_name.isidentifier()

        if agent_parameters is None:
            agent_parameters = {}
        if parameters is None:
            parameters = {}
        if number is not None:
            agent_parameters = [{} for _ in range(number)]

        self.sim_parameters.update(parameters)

        group = Group(self, self._processorgroup, [group_name], [AgentClass],
                      agent_arguments={'group': group_name,
                                       'trade_logging': self.trade_logging_mode,
                                       'database': self.database_queue,
                                       'check_unchecked_msgs': self.check_unchecked_msgs,
                                       'expiring': self.expiring,
                                       'perishable': self.perishable,
                                       'resource_endowment': self.resource_endowment})
        group.create_agents(agent_parameters=agent_parameters, **parameters)
        self.agents_created = True
        self._groups[group_name] = group
        self.messagess[group_name] = []
        return group

    def create_agents(self, AgentClass, group_name, simulation_parameters=None, agent_parameters=None, number=1):
        """ Creates an additional agent in an existing group during the simulation. If agents
        have been deleted, their id's are reduced.

        Args:

            AgentClass:
                the class of agent to create.
                (can be the same class as the creating agent)

            'group_name':
                the name of the group the agent should belong to. This is the
                group name string e.G. :code:`'firm'`, not the group variable e.G.
                :code:`firms` in :code:`firms = simulation.build_agents(...)`

            simulation_parameters:
                a dictionary of parameters

            agent_parameters:
                List of a dictionary of parameters

            number:
                if no agent_parameters list is given the number of agents to be created can be specified

        Returns:
           id of new agent.

        Example::

            self.create_agent(BeerFirm, 'beerfirm',
                              parameters=self.parameters,
                              agent_parameters={'creation': self.time})
        """
        if simulation_parameters is None:
            simulation_parameters = {}
        if agent_parameters is None:
            agent_parameters = [{}] * number
        group = self._groups[group_name]
        id = group.create_agents(simulation_parameters=simulation_parameters,
                                 agent_parameters=agent_parameters)
        return id

    def create_agent(self, AgentClass, group_name, simulation_parameters=None, agent_parameters=None):
        raise Exception("create_agent is depreciated for create_agents")

    def delete_agent(self, *ang):
        raise Exception("delete_agent is depreciated for create_agents")

    def delete_agents(self, group, ids):
        """ This deletes a group of agents. The model has to make sure that other
        agents are notified of the death of agents in order to stop them from corresponding
        with this agent. Note that if you create new agents
        after deleting agents the ID's of the deleted agents are reused.

        Args:
            group:
                group of the agent

            ids:
                a list of ids of the agents to be deleted in that group
        """
        group = self._groups[group]
        group.delete_agents(ids)

    def _write_description_file(self):
        description = open(os.path.abspath(
            self.path + '/description.txt'), 'w')
        description.write(json.dumps(self.sim_parameters,
                                     indent=4,
                                     skipkeys=True,
                                     default=lambda x: 'not_serializeable'))

    def _displaydescribtion(self):
        description = open(self.path + '/description.txt', 'r')
        print(description.read())

    def graphs(self):
        """ after the simulation is run, graphs() shows graphs of all data
        collected in the simulation. Shows the same output as the @gui
        decorator shows.


        Example::

            simulation = Simulation(...)
            for r in range(100):
                simulation.advance_round(r)
                agents.do_something()
                ...

            simulation.graphs()
        """
        self.finalize()
        graphs(self.sim_parameters)
