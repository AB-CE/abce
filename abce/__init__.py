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
import csv
import datetime
import os
import time
import multiprocessing as mp
from multiprocessing.managers import BaseManager
import abce.db
import abce.abcelogger
import postprocess
from glob import glob
from firmmultitechnologies import *
from household import Household
from agent import *
from collections import defaultdict, OrderedDict
from firm import Firm
from quote import Quote
import json
import abcegui
from family import Family
from abcegui import gui
import random
from abce.notenoughgoods import NotEnoughGoods


def execute_wrapper(inp):
    return inp[0].execute(inp[1], inp[2])

class MyManager(BaseManager):
    pass

class Simulation:
    """ This class in which the simulation is run. It takes
    the simulation_parameters to set up the simulation. Actions and agents have to be
    added. databases and resource declarations can be added. Then runs
    the simulation.

    Usually the parameters are specified in a tab separated csv file. The first
    line are column headers.

    Args::

     simulation_parameters: a dictionary with all parameters. "name" and
     "num_rounds" are mandatory.


    Example::

        simulation_parameters = {'num_rounds': 500}
        action_list = [
        ('household', 'recieve_connections'),
        ('household', 'offer_capital'),
        ('firm', 'buy_capital'),
        ('firm', 'production'),
        ('household', 'buy_product')
        'after_sales_before_consumption'
        ('household', 'consume')
        ]
        w = Simulation(simulation_parameters)
        w.add_action_list(action_list)
        w.build_agents(Firm, 'firm', 'num_firms')
        w.build_agents(Household, 'household', 'num_households')

        w.declare_round_endowment(resource='labor_endowment', productivity=1, product='labor')
        w.declare_round_endowment(resource='capital_endowment', productivity=1, product='capital')

        w.panel_data('firm', command='after_sales_before_consumption')

        w.run()
    """
    def __init__(self, rounds, name='abce', random_seed=None, trade_logging='off', cores=None, **chatch):
        """ This sets up the simulation.

        rounds:
            how many rounds the simulation lasts

        random_seed:
            Not implemented in this verion

        trade_logging:
            Whether trades are logged,trade_logging can be
            'group' (fast) or 'individual' (slow) or 'off'

        cores:
            The number of cores of your processor that are used for the simulation.
            Default is all your logical cores using hyper-threading when available.
            For easy debugging set cores to one and the simulation is executed
            without parallelization.
            Sometimes it is advisable to decrease the number of cores to the number
            of physical cores on your computer.
            'None' for all cores.

        Example::

            simulation = Simulation(rounds=1000, name='sim', trade_logging='individual', cores=None)

            or

            simulation = Simulation(**parameters, cores=None)
        """
        self.family_list = {}
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
        self._start_year = 0

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

        self.round = 0
        self.trade_logging_mode = trade_logging
        if self.trade_logging_mode not in ['individual', 'group', 'off']:
            SystemExit("trade_logging can be "
                       "'group' (fast) or 'individual' (slow) or 'off'"
                       ">" + self.trade_logging_mode + "< not accepted")

        manager = mp.Manager()
        self.database_queue = manager.Queue()
        self._db = abce.db.Database(self.path, self.database_queue, trade_log=self.trade_logging_mode != 'off')
        self.logger_queue = manager.Queue()

        if cores is None:
            self.cores = mp.cpu_count()
        else:
            self.cores = cores

        if random_seed is None or random_seed == 0:
            random_seed = time.time()
        random.seed(random_seed)

        self.sim_parameters = OrderedDict({'name': name, 'rounds': rounds, 'random_seed': random_seed})


    def add_action_list(self, action_list):
        """ add an `action_list`, which is a list of either:

        - tuples of an goup_names and and action
        - a single command string for panel_data or follow_agent
        - [tuples of an agent name and and action, currently not unit tested!]


        Example::

         action_list = [
            repeat([
                    ('Firm', 'sell'),
                    ('Household', 'buy')
                ],
                repetitions=10
            ),
            ('Household_03', 'dance')
            'panel_data_end_of_round_befor consumption',
            ('Household', 'consume'),
            ]
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
            raise SystemExit("WARNING: agents can not be build before declare_round_endowment")
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
            raise SystemExit("WARNING: agents can not be build before declare_perishable")
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
            raise SystemExit("WARNING: agents build before declare_expiring")
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

    def panel(self, group, possessions=[], variables=[]):
        """ panel(.) writes possessions and variables of a group of
            agents into the database.
            You must put ('agent_group', 'panel') in the action_list.

            Args:
                group:
                    can be either a group or 'all' for all agents
                possessions (list, optional):
                    a list of all possessions you want to track as 'strings'
                variables (list, optional):
                    a list of all variables you want to track as 'strings'

        Example in start.py::

         w.panel(group='firm', possessions=['money', 'input1'],
            variables=['production_target', 'gross_revenue'])
        """
        if len(self.family_list) > 0:
            raise SystemExit("WARNING: agents build before panel")
        self._db.add_panel(group)
        self.variables_to_track_panel[group] = variables
        self.possessins_to_track_panel[group] = possessions

    def aggregate(self, group, possessions=[], variables=[]):
        """ aggregate(.) writes summary statistics of variables and possessions
            of a group of agents into the database.
            You must put ('agent_group', 'panel') in the action_list.

            Args:
                group:
                    can be either a group or 'all' for all agents
                possessions (list, optional):
                    a list of all possessions you want to track as 'strings'
                variables (list, optional):
                    a list of all variables you want to track as 'strings'

        Example in start.py::

         w.aggregate(group='firm', possessions=['money', 'input1'],
            variables=['production_target', 'gross_revenue'])
        """
        if len(self.family_list) > 0:
            raise SystemExit("WARNING: agents build before aggregate")
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
                if not isinstance(action[0], tuple) and not isinstance(action[0], list):
                    try:
                        action = ((action[0],), action[1], action[2])
                    except IndexError:
                        action = ((action[0],), action[1])
                for group in action[0]:
                    assert group in self.family_list.keys(), \
                        '%s in (%s, %s) in the action_list is not a known agent' % (action[0], action[0], action[1])
                processed_list.append((self.execute, action[0], action[1]))
        return processed_list

    def execute_parallel(self, groups, command, messages):
        parameters = ((family, command, messages[family.name()]) for group in groups for family in self.family_list[group])
        families_messages = self.pool.map(execute_wrapper, parameters)
        for group in groups:
            for family in self.family_list[group]:
                messages[family.name()] = []
        for block in families_messages:
            for family_name, family_msgs in block.iteritems():
                if len(family_msgs):
                    messages[family_name].extend(family_msgs)
        return messages

    def execute_serial(self, groups, command, messages):
        families_messages = [execute_wrapper((family, command, messages[family.name()])) for group in groups for family in self.family_list[group]]
        for group in groups:
            for family in self.family_list[group]:
                messages[family.name()] = []
        for block in families_messages:
            for family_name, family_msgs in block.iteritems():
                if len(family_msgs):
                    messages[family_name].extend(family_msgs)
        return messages
    def execute_internal(self, command):
        for group in self.family_list:
            for family in self.family_list[group]:
                family.execute_internal(command)

    def run(self):
        """ This runs the simulation

            Args:
                parallel (False, True(default)):
                    Whether the agents' utility functions are executed in parallel.
                    For simulation that don't have hundreds of separate perishable
                    goods or resource False is faster.
        """
        if self.cores > 1:
            self.pool = mp.Pool(self.cores)
            self._db.start()
            self.execute = self.execute_parallel
        else:
            self.execute = self.execute_serial
        if not(self.family_list):
            raise SystemExit('No Agents Created')
        if not(self.action_list) and not(self._action_list):
            raise SystemExit('No action_list declared')
        if not(self._action_list):
            self._action_list = self._process_action_list(self.action_list)

        self._write_description_file()
        self._displaydescribtion()

        start_time = time.time()

        messagess = defaultdict(dict)

        messagess = {}
        self.family_names = []
        for group in self.family_list.values():
            for family in group:
                self.family_names.append(family.name())
                messagess[family.name()] = []
        try:
            for year in xrange(self._start_year, self.rounds):
                self.round = year
                print("\rRound" + str("%3d" % year))
                self.execute_internal('produce_resource')

                for processor, group, action in self._action_list:
                    messagess = processor(group, action, messagess)
                self.execute_internal('advance_round')
                self.execute_internal('perish')
        except:
            raise
        finally:
            print(str("time only simulation %6.2f" % (time.time() - start_time)))
            self.gracefull_exit()
            print(str("time with data and network %6.2f" % (time.time() - start_time)))
            postprocess.to_csv(os.path.abspath(self.path))
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

         w.build_agents(Firm, number=simulation_parameters['num_firms'])
         w.build_agents(Bank, parameters=simulation_parameters, agent_parameters=[{'name': UBS'},{'name': 'amex'},{'name': 'chase'})
         w.build_agents(CentralBank, number=1, parameters={'rounds': num_rounds})
        """
        assert number is None or agent_parameters is None, 'either set number or agent_parameters in build_agents'
        if number is not None:
            num_agents_this_group = number
            agent_parameters = [None] * num_agents_this_group
        else:
            num_agents_this_group = len(agent_parameters)

        self.family_list[group_name] = []

        MyManager.register('Family', Family)

        self.sim_parameters[group_name] = {key: parameter
                                           for key, parameter in parameters.iteritems()
                                           if key not in self.sim_parameters.keys() + ['trade_logging']}

        for i in range(min(self.cores, num_agents_this_group)):
            manager = MyManager()
            manager.start()
            family = manager.Family(AgentClass, num_agents_this_group=num_agents_this_group, batch=i, num_managers=self.cores,
                                    agent_args={'group': group_name,
                                                'trade_logging': self.trade_logging_mode,
                                                'database': self.database_queue,
                                                'logger':self.logger_queue,
                                                'random_seed': random.random()})

            for good, duration in self.expiring:
                family.declare_expiring(good, duration)

            try:
                family.init(parameters, agent_parameters)
            except AttributeError:
                print("Warning: agent has no init function")

            for good in self.perishable:
                family.register_perish(good)
            for resource, units, product in self.resource_endowment[group_name] + self.resource_endowment['all']:
                family.register_resource(resource, units, product)

            family.register_panel(self.possessins_to_track_panel[group_name],
                                  self.variables_to_track_panel[group_name])

            family.register_aggregate(self.possessions_to_track_aggregate[group_name],
                                      self.variables_to_track_aggregate[group_name])

            try:
                family.set_network_drawing_frequency(self._network_drawing_frequency)
            except AttributeError:
                family.set_network_drawing_frequency(None)

            self.family_list[group_name].append(family)

    def _write_description_file(self):
        description = open(os.path.abspath(self.path + '/description.txt'), 'w')
        description.write(json.dumps(self.sim_parameters, indent=4, skipkeys=True, default=lambda x: 'not_serializeable'))

    def _displaydescribtion(self):
        description = open(self.path + '/description.txt', 'r')
        print(description.read())

    def graphs(self):
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
        abcegui.run()

    def pickle(self, name):
        with open('%s.simulation' % name, 'wb') as jar:
            json.dump({'year': self.rounds,
                       'agents': [agent.__dict__ for agent in self.agents_list['all']],
                       'messages': self.messagess},
                      jar, default=handle_non_pickleable)

    def unpickle(self, name):
        with open('%s.simulation' % name, 'rb') as jar:
            simulation = json.load(jar)

        self._start_year = simulation['year']

        all_agents_values = simulation['agents']
        for agent, agent_values in zip(self.agents_list['all'], all_agents_values):
            for key, value in agent_values.iteritems():
                if value != "NotPickleable":
                    if key not in agent.__dict__:
                        agent.__dict__[key] =  value
                    elif isinstance(agent.__dict__[key], defaultdict):
                        try:
                            agent.__dict__[key] = defaultdict(type(value.values()[0]), value)
                        except IndexError:
                            agent.__dict__[key] = defaultdict(float)
                    elif isinstance(agent.__dict__[key], OrderedDict):
                        agent.__dict__[key] = OrderedDict(value)
                    elif isinstance(agent.__dict__[key], np.ndarray):
                        agent.__dict__[key] = np.array(value)
                    else:
                        agent.__dict__[key] =  value

        for agent in self.agents_list['all']:
            self.agents_list[agent.group][agent.idn] = agent

        self._messages = simulation['messages']

def handle_non_pickleable(x):
    if isinstance(x, np.ndarray):
        return list(x)
    else:
        return "NotPickleable"





class repeat:
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
