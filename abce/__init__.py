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


    parameters = {'name': 'name', num_rounds': 100}
    s = Simulation(parameters)
    action_list = [
    ('all', 'one'),
    ('all', 'two'),
    ('all', 'three'),
    ]
    s.add_action_list(action_list)
    s.build_agents(Agent, 2)
    s.run()
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


def execute_wrapper(inp):
    return inp[0].execute(inp[1], inp[2])

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

        simulation_parameters = {'num_rounds': 500}
        action_list = [
        ('household', 'recieve_connections'),
        ('household', 'offer_capital'),
        ('firm', 'buy_capital'),
        ('firm', 'production'),
        ('centralbank', 'intervention', lambda round: round == 250)
        ('household', 'buy_product')
        'after_sales_before_consumption'
        ('household', 'consume')
        ]
        w = Simulation(rounds=1000, name='sim', trade_logging='individual', processes=None)
        w.add_action_list(action_list)
        w.build_agents(Firm, 'firm', 'num_firms')
        w.build_agents(Household, 'household', 'num_households')

        w.declare_round_endowment(resource='labor_endowment', productivity=1, product='labor')
        w.declare_round_endowment(resource='capital_endowment', productivity=1, product='capital')

        w.panel_data('firm', command='after_sales_before_consumption')

        w.run()
    """
    def __init__(self, rounds, name='abce', random_seed=None, trade_logging='off', processes=None):
        """
        """
        self.family_list = {}
        self.num_of_agents_in_group = {}
        self._messages = {}
        self._action_list = []
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

        if processes is None:
            self.processes = mp.cpu_count() * 2
        else:
            self.processes = processes

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


    def add_action_list(self, action_list):
        """ add an `action_list`, which is a list of either:

        - tuples of an goup_names and and action: :code:`('firm', 'buying')`

        - tuples of an agent name and and action: :code:`(('firm', household), 'buying')`

        The tuples can have a condition under which they are execute. Only if this
        condition evaluates to True the tuple is executed.

        In the round mode (default), if an action is executed every 21 rounds
        or an intervention in round 50:::

            (('firm', household), 'buying', lambda round: round % 21 == 0)
            ('firm', 'buying', lambda round: round == 500)

        In the date mode::

            ('agent', 'wednessday', lambda date: date.weekday() == 2),  # Monday is 0
            ('agent', 'first', lambda date: date.day == 1),
            ('agent', 'newyearseve', lambda date: date.month == 12 and date.day == 31),
            ('agent', 'firstfriday', lambda date: date.day <= 7 and date.weekday() == 4),
            ('agent', 'fiveteens', lambda date: date.month == 15),
            ('agent', 'everythreedays', lambda date: date.toordinal() % 3 == 0),

        The date works like python's
        `date object <https://docs.python.org/2/library/datetime.html#date-objects>`_

        Example::

         action_list = [
            repeat([('firm', 'selling'),
                    (('firm', household), 'buying')], repetitions=10),
            ('household', 'dance'),
            ('household', 'consume')]
         w.add_action_list(action_list)
        """
        self.action_list = action_list

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
        if year is None:
            date = datetime.date.today()
        else:
            date = datetime.date(year, month, day)

        self._start_round = date.toordinal()
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

            action_list = [('firm', produce_and_sell),
                           ('firm', panel),
                           ('household', 'buying')]

            simulation_parameters.add_action_list(action_list)

            simulation_parameters.build_agents(Firm, 'firm', number=5)

            ...

            simulation.panel('firm', possessions=['money', 'input'],
                                     variables=['production_target', 'gross_revenue'])
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

            action_list = [('firm', produce_and_sell),
                           ('firm', aggregate),
                           ('household', 'buying')]

            simulation_parameters.add_action_list(action_list)

            simulation_parameters.build_agents(Firm, 'firm', number=5)

            ...

            simulation.aggregate('firm', possessions=['money', 'input'],
                                     variables=['production_target', 'gross_revenue'])
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

    def _process_action_list(self, action_list):
        processed_list = []
        for action in action_list:
            if isinstance(action, repeat):
                nested_action_list = self._process_action_list(action.action_list)
                for _ in range(action.repetitions):
                    processed_list.extend(nested_action_list)
            else:
                if len(action) == 2:
                    action = (action[0], action[1], lambda date: True)
                if not isinstance(action[0], tuple) and not isinstance(action[0], list):
                    try:
                        action = ((action[0],), action[1], action[2])
                    except IndexError:
                        action = ((action[0],), action[1])
                for group in action[0]:
                    assert group in list(self.family_list.keys()), \
                        '%s in (%s, %s) in the action_list is not a known agent' % (action[0], action[0], action[1])
                processed_list.append((action[0], action[1], action[2]))
        return processed_list

    def execute_parallel(self, groups, command, messages):
        parameters = ((family, command, messages[family.name()]) for group in groups for family in self.family_list[group])
        families_messages = self.pool.map(execute_wrapper, parameters, chunksize=1)
        for group in groups:
            for family in self.family_list[group]:
                messages[family.name()] = []
        messages[('_simulation', 0)] = []
        messages[('_simulation', 0.5)] = []
        for block in families_messages:
            for family_name, family_msgs in block.items():
                if len(family_msgs):
                    try:
                        messages[family_name].extend(family_msgs)
                    except KeyError:
                        raise KeyError("reciever of message, contract or similar not found "
                                       + str(family_name))
        return messages

    def execute_serial(self, groups, command, messages):
        families_messages = [execute_wrapper((family, command, messages[family.name()])) for group in groups for family in self.family_list[group]]
        for group in groups:
            for family in self.family_list[group]:
                messages[family.name()] = []
        messages[('_simulation', 0)] = []
        messages[('_simulation', 0.5)] = []
        for block in families_messages:
            for family_name, family_msgs in block.items():
                if len(family_msgs):
                    try:
                        messages[family_name].extend(family_msgs)
                    except KeyError:
                        raise KeyError("reciever of message, contract or similar not found "
                                       + str(family_name))
        return messages

    def execute_internal_seriel(self, command):
        for group in self.family_list:
            for family in self.family_list[group]:
                family.execute_internal(command)

    def execute_internal_parallel(self, command):
        parameters = ((family, command) for group in self.family_list for family in self.family_list[group])
        families_messages = self.pool.map(execute_internal_wrapper, parameters, chunksize=1)

    def run(self):
        """ This runs the simulation """
        if self.processes > 1:
            self.pool = mp.Pool(self.processes)
            self.execute = self.execute_parallel
            self.execute_internal = self.execute_internal_parallel
        else:
            self.execute = self.execute_serial
            self.execute_internal = self.execute_internal_seriel
        if not(self.family_list):
            raise SystemExit('No Agents Created')
        if not(self.action_list) and not(self._action_list):
            raise SystemExit('No action_list declared')
        if not(self._action_list):
            self._action_list = self._process_action_list(self.action_list)

        self._db.start()

        self._write_description_file()
        self._displaydescribtion()

        start_time = time.time()

        messagess = defaultdict(dict)

        messagess = {}
        self.family_names = []
        for group in list(self.family_list.values()):
            for family in group:
                self.family_names.append(family.name())
                messagess[family.name()] = []
        agents_to_add = []
        agents_to_delete = []
        try:
            for round in xrange(self._start_round, self._start_round + self.rounds):
                if self._calendar:
                    _round = datetime.date.fromordinal(round)
                    print("\rRound" + str(" %3d " % round) + str(_round))
                else:
                    print("\rRound" + str(" %3d " % round))
                    _round = round
                self.execute_internal('_produce_resource')

                for group, action, condition in self._action_list:
                    if condition(_round):
                        messagess = self.execute(group, action, messagess)
                        if messagess[('_simulation', 0)]:
                            agents_to_add.extend(messagess[('_simulation', 0)])
                            del messagess[('_simulation', 0)]
                        if messagess[('_simulation', 0.5)]:
                            agents_to_delete.extend(messagess[('_simulation', 0.5)])
                            del messagess[('_simulation', 0.5)]
                self.execute_internal('_advance_round')
                self.execute_internal('_perish')
                if agents_to_add:
                    self.add_agents(agents_to_add, round)
                    agents_to_add = []
                if agents_to_delete:
                    self.delete_agent(agents_to_delete)
                    agents_to_delete = []
        except EOFError:
            pass
        except:
            raise
        finally:
            self.round = round
            print(str("time only simulation %6.2f" % (time.time() - start_time)))
            self.gracefull_exit()
            print(str("time with data and network %6.2f" % (time.time() - start_time)))
            if self.round > 0:
                postprocess.to_csv(os.path.abspath(self.path), self._calendar)
                print(str("time with post processing %6.2f" % (time.time() - start_time)))
            self.messagess = messagess


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

         simulation.build_agents(Firm, number=simulation_parameters['num_firms'])
         simulation.build_agents(Bank, parameters=simulation_parameters, agent_parameters=[{'name': UBS'},{'name': 'amex'},{'name': 'chase'})
         simulation.build_agents(CentralBank, number=1, parameters={'rounds': num_rounds})
        """
        assert number is None or agent_parameters is None, 'either set number or agent_parameters in build_agents'
        if number is not None:
            num_agents_this_group = number
            agent_parameters = [None] * num_agents_this_group
        else:
            num_agents_this_group = len(agent_parameters)

        self.family_list[group_name] = []

        self.sim_parameters.update(parameters)

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
                                    agent_parameters=agent_parameters)

            for good, duration in self.expiring:
                family.declare_expiring(good, duration)

            for good in self.perishable:
                family.register_perish(good)

            for resource, units, product in self.resource_endowment[group_name] + self.resource_endowment['all']:
                family.register_resource(resource, units, product)

            family.register_panel(self.possessins_to_track_panel[group_name],
                                  self.variables_to_track_panel[group_name])

            family.register_aggregate(self.possessions_to_track_aggregate[group_name],
                                      self.variables_to_track_aggregate[group_name])

            family.set_network_drawing_frequency(self._network_drawing_frequency)

            self.family_list[group_name].append(family)
            self.num_of_agents_in_group[group_name] = num_agents_this_group

    def add_agents(self, messages, round):
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
                                                'start_round': round + 1})
            for good, duration in self.expiring:
                family.last_added_agent('_declare_expiring', (good, duration))

            family.last_added_agent('init', (parameters, agent_parameters))

            for good in self.perishable:
                family.last_added_agent('_register_perish', (good,))

            for resource, units, product in self.resource_endowment[group_name] + self.resource_endowment['all']:
                family.last_added_agent('_register_resource', (resource, units, product))

            family.last_added_agent('_register_panel', (self.possessins_to_track_panel[group_name],
                                                       self.variables_to_track_panel[group_name]))

            family.last_added_agent('_register_aggregate', (self.possessions_to_track_aggregate[group_name],
                                                       self.variables_to_track_aggregate[group_name]))

            try:
                family.last_added_agent('_set_network_drawing_frequency', (self._network_drawing_frequency,))
            except AttributeError:
                family.last_added_agent('_set_network_drawing_frequency', (None,))

    def delete_agent(self, messages):
        dest_family = defaultdict(list)
        for _, _, (group_name, id, quite) in messages:
            dest_family[(group_name, id % self.processes, quite)].append(id)

        for (group_name, family_id, quite), ids in dest_family.items():
            family = self.family_list[group_name][family_id]
            if quite:
                family.replace_with_dead(ids)
            else:
                family.remove(ids)



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

            w = Simulation(...)
            ...
            w.run()
            w.graphs()
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





class repeat(object):
    """ Repeats the contained list of actions several times

    Args:

     action_list:
        action_list that is repeated

     repetitions:
        the number of times that an actionlist is repeated

    Example with number of repetitions in simulation_parameters.csv::

        action_list = [
            repeat([
                    ('firm', 'sell'),
                    ('household', 'buy')
                ],
                repetitions=parameter['number_of_trade_repetitions']
            ),
            ('household_03', 'dance')
            'panel_data_end_of_round_before consumption',
            ('household', 'consume'),
            ]
        s.add_action_list(action_list)

    """
    def __init__(self, action_list, repetitions):
        self.action_list = action_list
        self.repetitions = repetitions


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
