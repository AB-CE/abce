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
#pylint: disable=W0212, C0111
""" The best way to start creating a simulation is by copying the start.py file
and other files from 'abce/template'.

To see how to create a simulation read :doc:`Walk_through`. In this module you
will find the explanation for the command.

This is a minimal template for a start.py::

    from __future__ import division  # makes / division work correct in python !
    from agent import Agent
    from abce import *


    simulation = Simulation(rounds=1000, name='sim')
    agents = simulation.build_agents(Agent, 'agent', 2)
    for round in simulation.next_round():
        agents.do('one')
        agents.do('two')
        agents.do('three')
    simulation.graphs()
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
import csv
import datetime
import os
import time
import multiprocessing as mp
from multiprocessing.managers import BaseManager
import abce.db
import abce.abcelogger
from . import postprocess
from glob import glob
from .firmmultitechnologies import *
from .household import Household
from .agent import *
from .group import Group
from collections import defaultdict, OrderedDict
from .firm import Firm
from .quote import Quote
from .contracting import Contracting
import json
from . import abcegui
from .family import Family
from .abcegui import gui
import random
from abce.notenoughgoods import NotEnoughGoods


def execute_internal_wrapper(inp):
    return inp[0].execute_internal(inp[1])

class MyManager(BaseManager):
    pass

class Simulation(object):
    """ This class in which the simulation is run. Actions and agents have to be
    added. databases and resource declarations can be added. Then runs
    the simulation.

    Args:
        rounds:
            how many rounds the simulation lasts

        random_seed (optional):
            a random seed that controls the random number of the simulation

        trade_logging:
            Whether trades are logged,trade_logging can be
            'group' (fast) or 'individual' (slow) or 'off'

        processes (optional):
            The number of processes that run in parallel. Each process hosts a share of
            the agents.
            Default is all your logical processor cores times two, using hyper-threading when available.
            For easy debugging set processes to one and the simulation is executed
            without parallelization.
            Sometimes it is advisable to decrease the number of processes to the number
            of logical or even physical processor cores on your computer.
            'None' for all processor cores times 2.
            **For easy debugging set processes to 1, this way only one agent runs at
            a time and only one error message is displayed**

        Example::

            simulation = Simulation(rounds=1000, name='sim', trade_logging='individual', processes=None)


    Example for a simulation::

        num_firms = 5
        num_households = 200000

        w = Simulation(rounds=1000, name='sim', trade_logging='individual', processes=None)

        w.declare_round_endowment(resource='labor_endowment', productivity=1, product='labor')
        w.declare_round_endowment(resource='capital_endowment', productivity=1, product='capital')

        w.panel_data('firm', command='after_sales_before_consumption')

        firms = w.build_agents(Firm, 'firm', num_firms)
        households = w.build_agents(Household, 'household', num_households)
        
        all = firms + households
        for round in w.next_round():
            households.do('recieve_connections'),
            households.do('offer_capital'),
            firms.do('buy_capital'),
            firms.do('production'),
            if round = 250:
                centralbank.do('intervention)
            households.do(buy_product')
            all.do('after_sales_before_consumption')
            households.do('consume')

        w.graphs()
    """
    def __init__(self, rounds, name='abce', random_seed=None, trade_logging='off', processes=None):
        """
        """
        self.family_list = {}
        self.num_of_agents_in_group = {}
        self._messages = {}
        self._resource_command_group = {}
        self._db_commands = {}
        self.num_agents = 0
        self._build_first_run = True
        self.resource_endowment = defaultdict(list)
        self.perishable = []
        self.expiring = []
        self.variables_to_track_panel = defaultdict(list)
        self.variables_to_track_aggregate = defaultdict(list)
        self.possessins_to_track_panel = defaultdict(list)
        self.possessions_to_track_aggregate = defaultdict(list)
        self._start_round = 0
        self.round = int(self._start_round)
        self._calendar = False
        self._network_drawing_frequency = 1  # this is default value as declared in self.network() method

        self.rounds = rounds

        try:
            os.makedirs(os.path.abspath('.') + '/result/')
        except OSError:
            pass

        self.path = (os.path.abspath('.') + '/result/' + name + '_' +
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
        """ the path variable contains the path to the simulation outcomes it can be used
        to generate your own graphs as all resulting csv files are there.
        """
        while True:
            try:
                os.makedirs(self.path)
                break
            except OSError:
                self.path += 'I'


        self.trade_logging_mode = trade_logging
        if self.trade_logging_mode not in ['individual', 'group', 'off']:
            SystemExit("trade_logging can be "
                       "'group' (fast) or 'individual' (slow) or 'off'"
                       ">" + self.trade_logging_mode + "< not accepted")

        manager = mp.Manager()
        self.database_queue = manager.Queue()
        self._db = abce.db.Database(self.path, self.database_queue, trade_log=self.trade_logging_mode != 'off')
        self.logger_queue = manager.Queue()

        self.processes = mp.cpu_count() * 2 if processes is None else processes

        MyManager.register('Family', Family)
        self.managers = []
        for i in range(self.processes):
            manager = MyManager()
            manager.start()

            self.managers.append(manager)

        if random_seed is None or random_seed == 0:
            random_seed = time.time()
        random.seed(random_seed)

        self.sim_parameters = OrderedDict({'name': name, 'rounds': rounds, 'random_seed': random_seed})

        if self.processes > 1:
            self.pool = mp.Pool(self.processes)
        self.execute_internal = self.execute_internal_parallel if self.processes > 1 else self.execute_internal_seriel
        self._agents_to_add = []  # container used in self.run
        self._agents_to_delete = []  # container used in self.run
        self.messagess = defaultdict(list)

    def setup(self):
        manager = mp.Manager()
        all_families = [item for sublist in self.family_list.values()
                        for item in sublist]


        for sender in all_families:
           for receiver in all_families:
                postbox = manager.list()  # same families in same manager can get the same manager.list()
                for _ in receiver.iter_agents():
                    postbox.append([])  # actually we need only sublists for agents actually in that family
                sender.register_send_postbox(postbox)
                receiver.register_receive_postbox(postbox)




    def declare_round_endowment(self, resource, units, product, groups=['all']):
        """ At the beginning of very round the agent gets 'units' units of good 'product' for
        every 'resource' he possesses.

        Round endowments can be group specific, that means that when somebody except
        this group holds them they do not produce. The default is 'all'.

        Args::

            resource:
                The good that you have to hold to get the other
            units:
                the multiplier to get the produced good
            product:
                the good that is produced if you hold the first good
            groups:
                a list of agent groups, which gain the second good, if they hold the first one

        Example::

            A farmer gets a ton of harvest for every acre:

            w.declare_round_endowment(resource='land', units=1000, product='wheat')


        """
        if len(self.family_list) > 0:
            raise Exception("WARNING: declare_round_endowment(...) must be called before the agents are build")
        for group in groups:
            self.resource_endowment[group].append((resource, units, product))

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
        if len(self.family_list) > 0:
            raise SystemExit("WARNING: declare_perishable(...) must be called before the agents are build")
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
        if len(self.family_list) > 0:
            raise SystemExit("WARNING: declare_expiring(...) must be called before the agents are build")
        self.expiring.append((good, duration))

    def declare_service(self, human_or_other_resource, units, service, groups=['all']):
        """ When the agent holds the human_or_other_resource, he gets 'units' of service every round
            the service can be used only with in this round.

        Args::

            human_or_other_resource:
                the good that needs to be in possessions to create the other good 'self.create('adult', 2)'
            units:
                how many units of the service is available
            service:
                the service that is created
            groups:
                a list of agent groups that can create the service

        Example::

            For example if a household has two adult family members, it gets 16 hours of work

            w.declare_service('adult', 8, 'work')
        """
        self.declare_round_endowment(human_or_other_resource, units, service, groups)
        self.declare_perishable(service)

    def declare_calendar(self, year=None, month=1, day=1):
        """ ABCE can run in two time model:

            rounds:
                As default ABCE runs in round mode. Agents can access the self.round
                variable to find out what round it is. The execution condition in the
                action_list is based on rounds.

            calendar:
                Every iteration over the action_list is a day. Agents can access
                self.date() to find out what date it is.

            Args:
               year, month, day

            Example::

                simulation.declare_calendar(2000, 1, 1)
                simulation.declare_calendar()  # starts at current date

        """
        if len(self.family_list) > 0:
            raise SystemExit("WARNING: declare_calendar(...) must be called before the agents are build")
        date = datetime.date.today() if year is None else datetime.date(year, month, day)

        self._start_round = date.toordinal()
        self.round = int(self._start_round)
        self._calendar = True

    def panel(self, group, possessions=[], variables=[]):
        """ panel(.) writes a panel of variables and possessions
            of a group of agents into the database, so that it is displayed
            in the gui. Aggregate must be declared before the agents are build.
            ('agent_group', 'panel') must be in the action_list, so that
            the simulation knows when to make the aggregate snapshot.

            Args:
                group:
                    can be either a group or 'all' for all agents
                possessions (list, optional):
                    a list of all possessions you want to track as 'strings'
                variables (list, optional):
                    a list of all variables you want to track as 'strings'

        Example in start.py::

            simulation_parameters.build_agents(Firm, 'firm', number=5)

            ...

            simulation.panel('firm', possessions=['money', 'input'],
                                     variables=['production_target', 'gross_revenue'])

            for round in simulation.next_round():
                firms.do('produce_and_sell)
                firms.do('panel')
                households.do('buying')
        """
        if len(self.family_list) > 0:
            raise SystemExit("WARNING: panel(...) must be called before the agents are build")
        self._db.add_panel(group)
        self.variables_to_track_panel[group] = variables
        self.possessins_to_track_panel[group] = possessions

    def aggregate(self, group, possessions=[], variables=[]):
        """ aggregate(.) writes summary statistics of variables and possessions
            of a group of agents into the database, so that it is displayed in
            the gui. Aggregate must be declared before the agents are build.
            ('agent_group', 'aggregate') must be in the action_list, so that
            the simulation knows when to make the aggregate snapshot.


            Args:
                group:
                    can be either a group or 'all' for all agents
                possessions (list, optional):
                    a list of all possessions you want to track as 'strings'
                variables (list, optional):
                    a list of all variables you want to track as 'strings'

        Example in start.py::


            simulation_parameters.build_agents(Firm, 'firm', number=5)

            ...

            simulation.aggregate('firm', possessions=['money', 'input'],
                                     variables=['production_target', 'gross_revenue'])

            for round in simulation.next_round():
                firms.do('produce_and_sell)
                firms.do('aggregate')
                households.do('buying')



        """
        if len(self.family_list) > 0:
            raise SystemExit("WARNING: aggregate(...) must be called before the agents are build")
        self._db.add_aggregate(group)
        self.variables_to_track_aggregate[group] = variables
        self.possessions_to_track_aggregate[group] = possessions

    def network(self, frequency=1, savefig=False, savegml=True,
                figsize=(24,20), dpi=100, pos_fixed=False, alpha=0.8):
        """ network(.) prepares abce to write network data.

        Args:
            frequency:
                the frequency with which the network is written, default=1
            savefig:
                wether to save a png file, default=False
            savegml:
                wether to save a gml file, default=True
            figsize:
               size of the graph in inch. (see matplotlib)
            dpi:
                resulution of the picture
            pos_fixed:
                positions are fixed after the first round

        Example::

            simulation.network(savefig=True)
        """
        self._network_drawing_frequency = frequency
        self._logger = abce.abcelogger.AbceLogger(self.path,
                                                  self.logger_queue,
                                                  savefig=savefig,
                                                  savegml=savegml,
                                                  figsize=figsize,
                                                  dpi=dpi,
                                                  pos_fixed=pos_fixed,
                                                  alpha=alpha)
        self._logger.start()


    def execute_internal_seriel(self, command):
        for group in self.family_list:
            for family in self.family_list[group]:
                family.execute_internal(command)

    def execute_internal_parallel(self, command):
        parameters = ((family, command) for group in self.family_list for family in self.family_list[group])
        families_messages = self.pool.map(execute_internal_wrapper, parameters, chunksize=1)

    def _prepare(self):
        """ This runs the simulation """
        if not(self.family_list):
            raise SystemExit('No Agents Created')

        self._db.start()

        self._write_description_file()
        self._displaydescribtion()

        self.clock = time.time()

    def next_round(self):
        if self.round - self._start_round == 0:  # the simulation has just started
            self._prepare()
        while self.rounds > self.round - self._start_round:
            if self.round > self._start_round:
                self._finalize_prev_round(self.round - 1)
            self._prepare_round(self.round)
            yield self.round
            self.round += 1
        if self.round - self._start_round == self.rounds:
            self._finalize()

    def _prepare_round(self, round):
        self._round = datetime.date.fromordinal(round) if self._calendar else round
        print("\rRound" + str(" %3d " % round) + str(self._round))
        self.execute_internal('_produce_resource')

    def _finalize_prev_round(self, round):
        self.execute_internal('_advance_round')
        self.add_agents(round)
        self.delete_agent()

    def gracefull_exit(self):
        self.database_queue.put('close')
        self.logger_queue.put(['close', 'close', 'close'])

        try:
            while self._logger.is_alive():
                time.sleep(0.05)
        except AttributeError:
            pass

        while self._db.is_alive():
            time.sleep(0.05)

        try:
            self.pool.close()
            self.pool.join()
        except AttributeError:
            pass

    def _finalize(self):
        print(str("time only simulation %6.2f" % (time.time() - self.clock)))
        self.gracefull_exit()
        print(str("time with data and network %6.2f" % (time.time() - self.clock)))
        if self.round > 0:
            postprocess.to_csv(os.path.abspath(self.path), self._calendar)
            print(str("time with post processing %6.2f" % (time.time() - self.clock)))

    def build_agents(self, AgentClass, group_name, number=None, parameters={}, agent_parameters=None):
        """ This method creates agents.

        Args:

            AgentClass:
                is the name of the AgentClass that you imported

            group_name:
                the name of the group, as it will be used in the action list and transactions.
                Should generally be lowercase of the AgentClass.

            number:
                number of agents to be created.

             group_name (optional):
                to give the group a different name than the lowercase
                class_name.

            parameters:
                a dictionary of parameters

            agent_parameters:
                a list of dictionaries, where each agent gets one dictionary.
                The number of agents is the length of the list

        Example::

         firms = simulation.build_agents(Firm, 'firm', number=simulation_parameters['num_firms'])
         banks = simulation.build_agents(Bank, 'bank', parameters=simulation_parameters, agent_parameters=[{'name': UBS'},{'name': 'amex'},{'name': 'chase'})
         centralbanks = simulation.build_agents(CentralBank, 'centralbank', number=1, parameters={'rounds': num_rounds})
        """
        assert number is None or agent_parameters is None, 'either set number or agent_parameters in build_agents'
        if number is not None:
            num_agents_this_group = number
            agent_parameters = [None] * num_agents_this_group
        else:
            num_agents_this_group = len(agent_parameters)

        self.family_list[group_name] = []

        self.sim_parameters.update(parameters)

        agent_params_from_sim = {'expiring':self.expiring,
                                 'perishable':self.perishable,
                                 'resource_endowment':self.resource_endowment[group_name] + self.resource_endowment['all'],
                                  'panel':(self.possessins_to_track_panel[group_name],
                                         self.variables_to_track_panel[group_name]),
                                  'aggregate':(self.possessions_to_track_aggregate[group_name],
                                    self.variables_to_track_aggregate[group_name]),
                                  'ndf':self._network_drawing_frequency}

        for i, manager in enumerate(self.managers):
            family = manager.Family(AgentClass,
                                    num_agents_this_group=num_agents_this_group,
                                    batch=i,
                                    num_managers=self.processes,
                                    agent_args={'group': group_name,
                                                'trade_logging': self.trade_logging_mode,
                                                'database': self.database_queue,
                                                'logger':self.logger_queue,
                                                'random_seed': random.random(),
                                                'start_round': self._start_round},
                                    parameters=parameters,
                                    agent_parameters=agent_parameters,
                                    agent_params_from_sim=agent_params_from_sim)
            self.family_list[group_name].append(family)
            self.num_of_agents_in_group[group_name] = num_agents_this_group
        return Group(self, [self.family_list[group_name]], group_name)

    def add_agents(self, round):
        messages = self._agents_to_add
        if len(messages) == 0:
            return
        for _, _, (AgentClass, group_name, parameters, agent_parameters) in messages:
            id = self.num_of_agents_in_group[group_name]
            self.num_of_agents_in_group[group_name] += 1
            assert len(self.family_list[group_name]) == self.processes, "the expandable parameter in build_agents must be set to true"
            family = self.family_list[group_name][id % self.processes]

            family.append(AgentClass, id=id,
                                    agent_args={'group': group_name,
                                                'trade_logging': self.trade_logging_mode,
                                                'database': self.database_queue,
                                                'logger':self.logger_queue,
                                                'random_seed': random.random(),
                                                'start_round': round + 1},
                                    parameters=parameters, agent_parameters=agent_parameters)
        self._agents_to_add = []

    def delete_agent(self):
        messages = self._agents_to_delete
        if len(messages) == 0:
            return
        dest_family = defaultdict(list)
        for _, _, (group_name, id, quite) in messages:
            dest_family[(group_name, id % self.processes, quite)].append(id)

        for (group_name, family_id, quite), ids in dest_family.items():
            family = self.family_list[group_name][family_id]
            if quite:
                family.replace_with_dead(ids)
            else:
                family.remove(ids)
        self._agents_to_delete = []



    def _write_description_file(self):
        description = open(os.path.abspath(self.path + '/description.txt'), 'w')
        description.write(json.dumps(self.sim_parameters, indent=4, skipkeys=True, default=lambda x: 'not_serializeable'))

    def _displaydescribtion(self):
        description = open(self.path + '/description.txt', 'r')
        print(description.read())

    def graphs(self, open=True, new=1):
        """ after the simulatio is run, graphs() shows graphs of all data
        collected in the simulation. Shows the same output as the @gui
        decorator shows.

        Args:

            open (True/False):
                whether to open a new window

            new:
                If new is 0, the url is opened in the same browser window if
                possible. If new is 1, a new browser window is opened if
                possible. If new is 2, a new browser page (tab) is opened
                if possible.

        Example::

            simulation = Simulation(...)
            for round in simulation.next_round():
                ...

            simulation.graphs()
        """
        if self.round > 0:
            abcegui.run(open=open, new=new)


    def pickle(self, name):
        with open('%s.simulation' % name, 'wb') as jar:
            json.dump({'year': self.rounds,
                       'agents': [agent.__dict__ for agent in self.num_of_agents_in_group['all']],
                       'messages': self.messagess},
                      jar, default=handle_non_pickleable)

    def unpickle(self, name):
        with open('%s.simulation' % name, 'rb') as jar:
            simulation = json.load(jar)

        self._start_round = simulation['year']

        all_agents_values = simulation['agents']
        for agent, agent_values in zip(self.num_of_agents_in_group['all'], all_agents_values):
            for key, value in agent_values.items():
                if value != "NotPickleable":
                    if key not in agent.__dict__:
                        agent.__dict__[key] =  value
                    elif isinstance(agent.__dict__[key], defaultdict):
                        try:
                            agent.__dict__[key] = defaultdict(type(list(value.values())[0]), value)
                        except IndexError:
                            agent.__dict__[key] = defaultdict(float)
                    elif isinstance(agent.__dict__[key], OrderedDict):
                        agent.__dict__[key] = OrderedDict(value)
                    elif isinstance(agent.__dict__[key], np.ndarray):
                        agent.__dict__[key] = np.array(value)
                    else:
                        agent.__dict__[key] =  value

        for agent in self.num_of_agents_in_group['all']:
            self.num_of_agents_in_group[agent.group][agent.id] = agent

        self._messages = simulation['messages']

def handle_non_pickleable(x):
    if isinstance(x, np.ndarray):
        return list(x)
    else:
        return "NotPickleable"


def _number_or_string(word):
    """ returns a int if possible otherwise a float from a string
    """
    try:
        return int(word)
    except ValueError:
        try:
            return float(word)
        except ValueError:
            return word
