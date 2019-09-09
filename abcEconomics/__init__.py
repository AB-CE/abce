# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# abcEconomics is open-source software. If you are using abcEconomics for your research you are
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
file and other files from 'abcEconomics/template' in https://github.com/AB-CE/examples.

To see how to create a simulation, read :doc:`ipython_tutorial`.


This is a minimal template for a start.py::

    from agent import Agent
    from abcEconomics import *


    simulation = Simulation(name='abcEconomics')
    agents = simulation.build_agents(Agent, 'agent', 2)
    for time in range(100):
        simulation.advance_round(time)
        agents.one()
        agents.two()
        agents.three()
    simulation.graphs()

Note two things are important: there must be either a

:func:`~abcEconomics.simulation.graphs` or a :func:`~abcEconomics.simulation.finalize` at the end
otherwise the simulation blocks at the end.
Furthermore, every round needs to be announced using simulation.advance_round(time),
where time is any representation of time.

"""
import re
import time
import random
import queue
import logging
import multiprocessing as mp
from collections import OrderedDict
from .logger import ThreadingDatabase, MultiprocessingDatabase
from .agent import Agent  # noqa: F401
from .group import Group
from .notenoughgoods import NotEnoughGoods  # noqa: F401
from .agents import Firm, Household  # noqa: F401
from .scheduler import SingleProcess, MultiProcess

try:
    # hack: make gui import optional
    from .gui import gui, graph  # noqa: F401
except Exception:
    pass


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

        path:
            path for database use None to omit directory creation.

        dbplugin, dbpluginargs:
            database plugin, see :ref:`Database Plugins`

        Example::

            simulation = Simulation(name='abcEconomics',
                                    trade_logging='individual',
                                    processes=None)


    Example for a simulation::

        num_firms = 5
        num_households = 2000

        w = Simulation(name='abcEconomics',
                       trade_logging='individual',
                       processes=None)

        w.panel('firm', command='after_sales_before_consumption')

        firms = w.build_agents(Firm, 'firm', num_firms)
        households = w.build_agents(Household, 'household', num_households)

        all = firms + households

        for time in range(100):
            self.time = time
            endowment.refresh_services('labor', derived_from='labor_endowment', units=5)
            households.recieve_connections()
            households.offer_capital()
            firms.buy_capital()
            firms.production()
            if time == 250:
                centralbank.intervention()
            households.buy_product()
            all.after_sales_before_consumption()
            households.consume()

        w.finalize()
        w.graphs()
    """

    def __init__(self, name='abcEconomics', random_seed=None, trade_logging='off', processes=1, dbplugin=None,
                 dbpluginargs=[], path='auto', multiprocessing_database=False):
        """
        """
        try:
            name = simulation_name  # noqa: F821
        except NameError:
            pass

        self.agents_created = False
        self.resource_endowment = []

        self.trade_logging_mode = trade_logging
        if self.trade_logging_mode not in ['individual', 'group', 'off']:
            Exception("trade_logging can be "
                      "'group' (fast) or 'individual' (slow) or 'off'"
                      ">" + self.trade_logging_mode + "< not accepted")

        self.processes = mp.cpu_count() * 2 if processes is None else processes

        if processes == 1:
            self.scheduler = SingleProcess()
        else:
            self.scheduler = MultiProcess(processes)

        if processes == 1 and not multiprocessing_database:
            self.database_queue = queue.Queue()
        else:
            manager = mp.Manager()
            self.database_queue = manager.Queue()

        if multiprocessing_database:
            Database = MultiprocessingDatabase
        else:
            Database = ThreadingDatabase

        self._db = Database(
            path,
            name,
            self.database_queue,
            trade_log=self.trade_logging_mode != 'off',
            plugin=dbplugin,
            pluginargs=dbpluginargs)
        self.path = self._db.directory
        self._db.start()

        if random_seed is None or random_seed == 0:
            random_seed = time.time()
        random.seed(random_seed)

        self.sim_parameters = OrderedDict(
            {'name': name, 'random_seed': random_seed})
        self.clock = time.time()
        self._time = None
        """ The current time set with simulation.advance_round(time)"""
        self._groups = {}
        """ A list of all agent names in the simulation """

    @property
    def time(self):
        """ Set and get time for simulation and all agents """
        return self._time

    @time.setter
    def time(self, time):
        """ Set and get time for simulation and all agents """
        self.advance_round(time)

    def advance_round(self, time):
        self._time = time
        logging.debug("\rRound" + str(time))
        str_time = re.sub('[^0-9a-zA-Z_]', '', str(time))
        self.scheduler.advance_round(time, str_time)

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
        print('')
        print("time only simulation %6.2f" %
              (time.time() - self.clock))

        self._db.finalize(self.sim_parameters)

        try:
            self.pool.close()
            self.pool.join()
        except AttributeError:
            pass

        print("time with data %6.2f" %
              (time.time() - self.clock))

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
        assert number is not None or agent_parameters is not None, \
            'please set either the number or agent_parameters in build_agents'
        assert group_name.isidentifier()

        if agent_parameters is None:
            agent_parameters = {}
        if parameters is None:
            parameters = {}
        if number is not None:
            agent_parameters = [{} for _ in range(number)]

        self.sim_parameters[group_name] = parameters

        group = Group(self, self.scheduler, None,
                      agent_arguments={'group': group_name,
                                       'trade_logging': self.trade_logging_mode,
                                       'database': self.database_queue})
        group.create_agents(AgentClass, agent_parameters=agent_parameters, **parameters)
        self.agents_created = True
        self._groups[group_name] = group
        return group

    def create_agents(self, AgentClass, group_name, simulation_parameters=None, agent_parameters=None, number=1):

        raise Exception("create_agents is depreciated for Group.create_agents")

    def create_agent(self, AgentClass, group_name, simulation_parameters=None, agent_parameters=None):
        raise Exception("create_agent is depreciated for Group.create_agents")

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

    def graph(self):
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
        graph(self.sim_parameters)
