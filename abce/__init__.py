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


    for parameters in read_parameters('simulation_parameters.csv'):
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
import csv
import datetime
import os
import sys
import time
import inspect
from abce.tools import agent_name, group_address
import multiprocessing as mp
import abce.db
import abce.abcelogger
import itertools
import postprocess
from glob import glob
from firm import Firm
from firmmultitechnologies import *
from household import *
from agent import *
from abce.communication import Communication
from copy import copy
from collections import defaultdict

BASEPATH = os.path.dirname(os.path.realpath(__file__))


def read_parameters(parameters_file='simulation_parameters.csv'):
    """ reads a parameter file line by line and gives a list. Where each line
    contains all parameters for a particular run of the simulation.

    Args:

        parameters_file (optional):
            filename of the csv file. (default:`simulation_parameters.csv`)

        delimiter (optional):
            delimiter of the csv file. (default: tabs)

        quotechar (optional):
            for single entries that contain the delimiter. (default: ")
            See python csv lib http://docs.python.org/library/csv.html


    This code reads the file and runs a simulation for every line::

     for parameter in read_parameters('simulation_parameters.csv'):
        w = Simulation(parameter)
        w.build_agents(Agent, 'agent', 'num_agents')
        w.run()
    """
    start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    parameter_array = []

    csvfile = open(parameters_file)
    dialect = csv.Sniffer().sniff(csvfile.read(1024))
    csvfile.seek(0)
    reader = csv.reader(csvfile, dialect)

    keys = [key.lower() for key in reader.next()]
    for line in reader:
        if line == []:
            continue
        cells = [_number_or_string(cell.lower()) for cell in line]
        parameter = dict(zip(keys, cells))
        if 'num_rounds' not in keys:
            raise SystemExit('No "num_rounds" column in ' + parameters_file)
        if 'name' not in parameter:
            try:
                parameter['name'] = parameter['Name']
            except KeyError:
                print("no 'name' (lowercase) column in " + parameters_file)
                parameter['name'] = 'abce'
        parameter['name'] = str(parameter['name']).strip("""\"""").strip("""\'""")
        try:
            if parameter['random_seed'] == 0:
                parameter['random_seed'] = None
        except KeyError:
            parameter['random_seed'] = None
        parameter['_path'] = os.path.abspath('./result/' + parameter['name'] + '_' + start_time)
        try:
            os.makedirs('./result/')
        except OSError:
            pass
        try:
            os.makedirs(parameter['_path'])
        except OSError:
            files = glob(parameter['_path'] + '/*')
            for file_to_remove in files:
                os.remove(file_to_remove)
        for key in parameter:
            if key == '' or key[0] == '#' or key[0] == '_':
                del key
        parameter_array.append(parameter)
    return parameter_array


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
     for simulation_parameters in read_parameters('simulation_parameters.csv'):
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
    def __init__(self, simulation_parameters):
        self.simulation_parameters = simulation_parameters
        self.agent_list = {}
        self.agent_list['all'] = []
        self.agents_backend = {}
        self.agents_backend['all'] = []
        self.agents_command_socket = {}
        self.agents_command_socket['all'] = []
        self._action_list = []
        self._resource_command_group = {}
        self._db_commands = {}
        self.num_agents = 0
        self.num_agents_in_group = {}
        self._build_first_run = True
        self._agent_parameters = None
        self.database_name = 'database'
        self.resource_endowment = defaultdict(list)
        self.perishable = []
        self.variables_to_track = defaultdict(list)

        self._communication = Communication()
        self.communication_frontend, self.communication_backend, self.ready = self._communication.get_queue()
        self.database_queue = mp.Queue()
        self._db = abce.db.Database(simulation_parameters['_path'], self.database_name, self.database_queue)
        self.logger_queue = mp.Queue()
        self._logger = abce.abcelogger.AbceLogger(simulation_parameters['_path'], self.logger_queue)
        self._logger.start()

        self.round = 0
        try:
            self.trade_logging_mode = simulation_parameters['trade_logging'].lower()
        except KeyError:
            self.trade_logging_mode = 'individual'
            print("'trade_logging' in simulation_parameters.csv not set"
                  ", default to 'individual', possible values "
                  "('group' (fast) or 'individual' (slow) or 'off')")
        if not(self.trade_logging_mode in ['individual', 'group', 'off']):
            print(type(self.trade_logging_mode), self.trade_logging_mode, 'error')
            SystemExit("'trade_logging' in simulation_parameters.csv can be "
                       "'group' (fast) or 'individual' (slow) or 'off'"
                       ">" + self.trade_logging_mode + "< not accepted")
        assert self.trade_logging_mode in ['individual', 'group', 'off']

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

    def add_action_list_from_file(self, parameter):
        """ The action list can also be declared in the simulation_parameters.csv
        file. Which allows you to run a batch of simulations with different
        orders. In simulation_parameters.csv there must be a column with which
        contains the a declaration of the action lists:

        +-------------+-------------+--------------------------------------------+-----------+
        | num_rounds  | num_agents  | action_list                                | endowment |
        +=============+=============+============================================+===========+
        | 1000,       | 10,         | [ ('firm', 'sell'), ('household', 'buy')], | (5,5)     |
        +-------------+-------------+--------------------------------------------+-----------+
        | 1000,       | 10,         | [ ('firm', 'buf'), ('household', 'sell')], | (5,5)     |
        +-------------+-------------+--------------------------------------------+-----------+
        | 1000,       | 10,         | [ ('firm', 'sell'),                        |           |
        |             |             | ('household', 'calculate_net_wealth'),     |           |
        |             |             | ('household', 'buy')],                     | (5,5)     |
        +-------------+-------------+--------------------------------------------+-----------+

        The command::

            self.add_action_list_from_file('parameters['action_list'])

        Args::

            parameter
                a string that contains the action_list. The string can be read
                from the simulation_parameters file: parameters['action_list'], where action_list
                is the column header in simulation_parameters.


        """
        self.add_action_list(eval(parameter))
        #TODO test


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
        if len(self.agent_list['all']) > 0:
            print("WARNING: agents build before declare_perishable")
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
        if len(self.agent_list['all']) > 0:
            print("WARNING: agents build before declare_perishable")
        self.perishable.append(good)


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

    #TODO also for other variables
    def panel(self, group, variables=[]):
        """ Panel_data writes variables of a group of agents into the database.
            It always writes all possessions of the agent. With the optional
            parameter variables you can insert (as strings) additional variables,
            to be tracked.
            You must put ('agent_group', 'panel') in the action_list.

            Args:
                group:
                    can be either a group or 'all' for all agents
                variables (list, optional):
                    a list of all variables you want to track as 'strings'

        Example in start.py::

         w.panel_data(group='firm', variables=['production_target', 'gross_revenue'])

         or

         w.panel_data(group=firm)
        """
        if len(self.agent_list['all']) > 0:
            print("WARNING: agents build before declare_perishable")
        self._db.add_panel(group)
        self.variables_to_track[group].append(variables)

    def _process_action_list(self, action_list):
        processed_list = []
        for action in action_list:
            if type(action) is tuple:
                if action[0] not in self.num_agents_in_group.keys() + ['all']:
                    SystemExit('%s in (%s, %s) in the action_list is not a known agent' % (action[0], action[0], action[1]))
                processed_list.append((action[0], action[1]))
            elif isinstance(action, repeat):
                nested_action_list = self._process_action_list(action.action_list)
                for _ in range(action.repetitions):
                    processed_list.extend(nested_action_list)
            else:
                processed_list.append(('all', action))
        return processed_list

    def run(self):
        """ This runs the simulation """
        if not(self.agent_list):
            raise SystemExit('No Agents Created')
        if not(self.action_list) and not(self._action_list):
            raise SystemExit('No action_list declared')
        if not(self._action_list):
            self._action_list = self._process_action_list(self.action_list)

        for agent in self.agent_list['all']:
            agent.start()
        self._db.start()
        self._communication.set_agents(self.agents_backend)
        self._communication.start()
        self.ready.recv()

        self._write_description_file()
        self._displaydescribtion()

        start_time = time.time()

        for year in xrange(self.simulation_parameters['num_rounds']):
            self.round = year
            print("\rRound" + str("%3d" % year)),

            for queue in self.agents_command_socket['all']:
                queue.send('_produce_resource')

            for group, action in self._action_list:
                self._add_agents_to_wait_for(len(self.agents_command_socket[group]))
                for queue in self.agents_command_socket[group]:
                    queue.send(action)
                self._wait_for_agents()

            for queue in self.agents_command_socket['all']:
                queue.send('_advance_round')
            for queue in self.agents_command_socket['all']:
                queue.send('_perish')

        print(str("%6.2f" % (time.time() - start_time)))
        self.gracefull_exit()

    def gracefull_exit(self):
        for queue in self.agents_command_socket['all']:
            queue.send("_die")
        for agent in list(itertools.chain(*self.agent_list.values())):
            while agent.is_alive():
                time.sleep(0.1)
        self._end_Communication()
        self.database_queue.put('close')
        self.logger_queue.put('close')
        while self._db.is_alive():
            time.sleep(0.05)
        while self._communication.is_alive():
            time.sleep(0.025)
        postprocess.to_csv(os.path.abspath(self.simulation_parameters['_path']), self.database_name)

    def build_agents(self, AgentClass,  number=None, group_name=None, agent_parameters=None):
        """ This method creates agents, the first parameter is the agent class.
        "num_agent_class" (e.G. "num_firm") should be difined in
        simulation_parameters.csv. Alternatively you can also specify number = 1.s

        Args::

         AgentClass: is the name of the AgentClass that you imported
         number (optional): number of agents to be created. or the colum name
         of the row in simulation_parameters.csv that contains this number. If not
         specified the column name is assumed to be 'num_' + agent_name
         (all lowercase). For example num_firm, if the class is called
         Firm or name = Firm.
         [group_name (optional): to give the group a different name than the
         class_name. (do not use this if you have not a specific reason]

        Example::

         w.build_agents(Firm, number='num_firms')
         # 'num_firms' is a column in simulation_parameters.csv
         w.build_agents(Bank, 1)
         w.build_agents(CentralBank, number=1)
        """
        #TODO single agent groups get extra name without number
        #TODO when there is a group with a single agent the ask_agent has a confusingname
        if not(group_name):
            group_name = AgentClass.__name__.lower()
        if number and not(agent_parameters):
            try:
                num_agents_this_group = int(number)
            except ValueError:
                try:
                    num_agents_this_group = self.simulation_parameters[number]
                except KeyError:
                    SystemExit('build_agents ' + group_name + ': ' + number +
                    ' is not a number or a column name in simulation_parameters.csv'
                    'or the parameterfile you choose')
        elif not(number) and not(agent_parameters):
            try:
                num_agents_this_group = self.simulation_parameters['num_' + group_name.lower()]
            except KeyError:
                raise SystemExit('num_' + group_name.lower() + ' is not in simulation_parameters.csv')
        elif not(number) and agent_parameters:
            num_agents_this_group = len(agent_parameters)
            self.simulation_parameters['num_' + group_name.lower()] = num_agents_this_group
        else:
            raise SystemExit('build_agents ' + group_name + ': Either '
                'number_or_parameter_column or agent_parameters must be'
                'specied, NOT both.')
        if not(agent_parameters):
            agent_parameters = [None for _ in range(num_agents_this_group)]

        self.num_agents += num_agents_this_group
        self.num_agents_in_group[group_name] = num_agents_this_group
        self.num_agents_in_group['all'] = self.num_agents
        self.agent_list[group_name] = []
        self.agents_backend[group_name] = []
        self.agents_command_socket[group_name] = []

        for idn in range(num_agents_this_group):
            commands_recv, commands_send = mp.Pipe(duplex=False)
            backend_recv, backend_send = mp.Pipe(duplex=False)
            agent = AgentClass(simulation_parameters=self.simulation_parameters,
                               agent_parameters=agent_parameters[idn],
                               idn=idn,
                               commands=commands_recv,
                               group=group_name,
                               trade_logging=self.trade_logging_mode,
                               database=self.database_queue,
                               logger=self.logger_queue,
                               backend_recv=backend_recv,
                               backend_send=backend_send,
                               frontend=self.communication_frontend)
            agent.name = agent_name(group_name, idn)
            for good in self.perishable:
                agent._register_perish(good)
            for resource, units, product in self.resource_endowment[group_name] + self.resource_endowment['all']:
                agent._register_resource(resource, units, product)
            for variables in self.variables_to_track[group_name] + self.variables_to_track['all']:
                agent._register_panel(variables)
            self.agent_list[group_name].append(agent)
            self.agent_list['all'].append(agent)
            self.agents_backend[group_name].append(backend_send)
            self.agents_backend['all'].append(backend_send)
            self.agents_command_socket[group_name].append(commands_send)
            self.agents_command_socket['all'].append(commands_send)

    def build_agents_from_file(self, AgentClass, parameters_file=None, multiply=1):
        """ This command builds agents of the class AgentClass from an csv file.
        This way you can build agents and give every single one different
        parameters.

        The file must be tab separated. The first line contains the column
        headers. The first column "agent_class" specifies the agent_class. The
        second column "number" (optional) allows you to create more than one
        agent of this type. The other columns are parameters that you can
        access in own_parameters the __init__ function of the agent.

        Agent created from a csv-file::

         class Agent(AgentEngine):
            def __init__(self, simulation_parameter, own_parameters, _pass_to_engine):
                AgentEngine.__init__(self, *_pass_to_engine)
                self.size = own_parameters['firm_size']
        """
        #TODO declare all self.simulation_parameters['num_XXXXX'], when this is called the first time
        if parameters_file == None:
            try:
                parameters_file = self.simulation_parameters['agent_parameters_file']
            except KeyError:
                parameters_file = 'agent_parameters.csv'
        elif self._agent_parameters == None:
            if parameters_file != self._agent_parameters:
                SystemExit('All agents must be declared in the same agent_parameters.csv file')
        self._agent_parameters = parameters_file

        agent_class = AgentClass.__name__.lower()
        agent_parameters = []
        csvfile = open(parameters_file)
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        agent_file = csv.reader(csvfile, dialect)
        keys = [key for key in agent_file.next()]
        if not(set(('agent_class', 'number')).issubset(keys)):
            SystemExit(parameters_file + " does not have a column 'agent_class'"
                "and/or 'number'")

        agents_list = []
        for line in agent_file:
            cells = [_number_or_string(cell) for cell in line]
            agents_list.append(dict(zip(keys, cells)))

        if self._build_first_run:
            for line in agents_list:
                num_entry = 'num_' + line['agent_class'].lower()
                if num_entry not in self.simulation_parameters:
                    self.simulation_parameters[num_entry] = 0
                self.simulation_parameters[num_entry] += int(line['number'])
            self._build_first_run = False

        for line in agents_list:
            if line['agent_class'] == agent_class:
                agent_parameters.extend([line for _ in range(line['number'] * multiply)])

        self.build_agents(AgentClass, agent_parameters=agent_parameters)

    def _add_agents_to_wait_for(self, number):
        self.communication_frontend.put(['+', str(number)])

    def _wait_for_agents(self):
        try:
            self.ready.recv()
        except KeyboardInterrupt:
            self.gracefull_exit()
            sys.exit(-1)

    def _end_Communication(self):
        self.communication_frontend.put(['+', 'end_Communication'])

    def _write_description_file(self):
        description = open(
                os.path.abspath(self.simulation_parameters['_path'] + '/description.txt'), 'w')
        description.write('\n')
        description.write('\n')
        for key in self.simulation_parameters:
            description.write(key + ": " + str(self.simulation_parameters[key]) + '\n')

    def _displaydescribtion(self):
        description = open(self.simulation_parameters['_path'] + '/description.txt', 'r')
        print(description.read())




class repeat:
    """ Repeats the contained list of actions several times

    Args:

     action_list:
        action_list that is repeated

     repetitions:
        the number of times that an actionlist is repeated or the name of
        the corresponding parameter in simulation_parameters.csv

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


class repeat_while:
    """ NOT IMPLEMENTED Repeats the contained list of actions until all agents_risponed
    done. Optional a maximum can be set.

    Args::

     action_list: action_list that is repeated
     repetitions: the number of times that an actionlist is repeated or the name of
     the corresponding parameter in simulation_parameters.csv

    """
    #TODO implement into _process_action_list
    def __init__(self, action_list, repetitions=None):
        SystemExit('repeat_while not implement yet')
        self.action_list = action_list
        if repetitions:
            try:
                self.repetitions = int(repetitions)
            except ValueError:
                try:
                    self.repetitions = self.simulation_parameters[repetitions]
                except KeyError:
                    SystemExit('add_action_list/repeat ' + repetitions + ' is not a number or'
                               'a column name in simulation_parameters.csv or the parameterfile'
                               'you choose')
        else:
            self.repetitions = None
        raise SystemExit('repeat_while not implemented')
        #TODO implement repeat_while




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


