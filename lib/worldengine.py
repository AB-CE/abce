"""
File needs to be a tab separated. First row has column headings. Each following
line is one simulation; Fileds in this file are variables you can access in
world during the simulation. self.column_header

    necessary fields:
    'name': name of the simulation
    'number_of_rounds': number of rounds of this simulation
    optional:
    random_seed: random seed 0 or missing chooses a random_seed at random
"""
import csv
import datetime
import os
import time
import zmq
import inspect
from abce_common import agent_name, group_address
import multiprocessing
import abce_db
import itertools
import pyparsing as pp


def read_parameters(parameter_file='world_parameters.csv', delimiter='\t', quotechar='"'):
    """ reads a parameter file line by line and gives a list. Where each line
    contains all parameters for a particular run of the simulation.

    Args::
    parameter_file (optional): filename of the csv file.
                    default:'world_parameters.csv'
    delimiter (optional): delimiter of the csv file.
                    default: tabs
    quotechar (optional): for single entries that contain the delimiter.
                    default: "
                    See python csv lib http://docs.python.org/library/csv.html


    This code reads the file and runs a simulation for every line::

     for parameter in world.read_parameters('world_parameters.csv'):
        w = world.World(parameter)
        w.build_agents(Agent, 'agent', 'number_of_agents')
        w.run()
    """
    start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    start_time_compact = datetime.datetime.now().strftime("%y%m%d%H%M")
    parameter_array = []
    reader = csv.reader(open(parameter_file),
                                delimiter=delimiter, quotechar=quotechar)
    keys = [key for key in reader.next()]
    for line in reader:
        cells = [_number_or_string(cell) for cell in line]
        parameter = dict(zip(keys, cells))
        if ('name' not in keys) and ('Name' not in keys) or 'number_of_rounds' not in keys:
            raise SystemExit('No "name" or "number_of_rounds" column in ' + parameter_file)
        if 'name' not in parameter:
            parameter['name'] = parameter['Name']

        try:
            parameter['name'] = parameter['name'].strip("""\"""").strip("""\'""")
        except KeyError:
            print("no 'name' (lowercase) column in " + parameter_file)
            parameter['name'] = 'abce'
        try:
            if parameter['random_seed'] == 0:
                parameter['random_seed'] = None
        except KeyError:
            parameter['random_seed'] = None
        parameter['_path'] = './result/' + parameter['name'] + '_' + start_time
        try:
            os.makedirs('./result/')
        except OSError:
            pass
        try:
            os.makedirs(parameter['_path'])
        except OSError:
            parameter['_path'] = parameter['_path'] + 'a'
            os.makedirs(parameter['_path'])
        for key in parameter:
            if key == '' or key[0] == '#' or key[0] == '_':
                del key
        parameter_array.append(parameter)
    return parameter_array
    #TODO put the initialisation in the init so that it can eat a dict

class WorldEngine:
    """ This class is the world in which the simulation is run. It takes
    the world_parameters to set up the world. Actions and agents have to be
    added. databases and resource declarations can be added. Than run runs
    the simulation.

    Usually the parameters are specified in a tab separated csv file. The first
    line are column headers.

    Args::

     world_parameters: a dictionary with all parameters. "name" and
     "number_of_rounds" are mandatory.


    Example::
     for world_parameters in world.read_parameters('world_parameters.csv'):
        action_list = [
        ('household', 'recieve_connections'),
        ('household', 'offer_capital'),
        ('firm', 'buy_capital'),
        ('firm', 'production'),
        ('household', 'buy_product')
        'after_sales_before_consumption'
        ('household', 'consume')
        ]
        w = world.World(world_parameters)
        w.add_action_list(action_list)
        w.build_agents(Firm, 'firm', 'number_of_firms')
        w.build_agents(Household, 'household', 'number_of_households')

        w.declare_resource(resource='labor_endowment', productivity=1, product='labor')
        w.declare_resource(resource='capital_endowment', productivity=1, product='capital')

        w.panel_db('firm', command='after_sales_before_consumption')

        w.run()




    """
    def __init__(self, world_parameters):
        self.parameter = world_parameters
        self._action_groups = {}
        self.agent_list = {}
        self._action_list = []
        self._resource_commands = {}
        self._perish_commands = {}
        self._resource_command_group = {}
        self._db_commands = {}
        self._db_follow_agent = {}
        self.num_agents = 0
        self.num_agents_in_group = {}
        self.context = zmq.Context()
        self.commands = self.context.socket(zmq.PUB)
        _Communication().start()
        time.sleep(1)  #TODO
        self.__command_addresse = "ipc://commands.ipc"
        self.commands.bind(self.__command_addresse)
        self.ready = self.context.socket(zmq.PULL)
        self.ready.connect("ipc://ready.ipc")
        self.communication_channel = self.context.socket(zmq.PUSH)
        self.communication_channel.connect("ipc://frontend.ipc")
        time.sleep(1)  #TODO
        self._register_action_groups()
        self._db = abce_db.Database(world_parameters['_path'], 'database')

    def add_action_list(self, action_list):
        """ add a list of actions: Either::
         tuples of an goup_names and and action
         tuples of an agent name and and action
         a single command string for panel_db or follow_db


        Example::
         action_list = [
            ('firm', 'sell'),
            ('household', 'buy'),
            ('household_03', 'dance')
            'panel_db_end_of_round_befor consumption',
            ('household', 'consume'),
            ]
         w.add_action_list(action_list)
        """
        self.action_list = action_list

    def add_action_list_from_file(self, action_list_file='action_list.csv'):
        """ alternative to add_action_list(...) reads the action_list from the
        parameter file. Reads the action list from a file. The file has one
        entry per row! Every row has either a command for panel_db or follow_db.
        Or a tuple to send a command to a group.
        "self.action_list =" and sqare brackets are optional

        You can use this to make a batch operation with different action lists
        in every simulation.

        //see also add_action_list(...)

        Args::
         action_list_file (optional): name of the file. default: 'action_list.csv'

        Example action_list.csv:

         action_list = [
            ('firm', 'sell'),
            ('household', 'buy'),
            'panel_db_end_of_round_befor consumption',
            ('household', 'consume'),
            ]

        Example many simulations::

         in 'world_parameters.csv', there is a column 'action_list_file_name'
         specfing a different action_list per simulation. The corresponding
         files exist.

         ...
         w.add_action_list_from_file(parameter['action_list_file_name'])
         ...
        """
        S = pp.Suppress
        Ot = pp.Optional
        before = Ot('self') + Ot('.') + Ot('action_list') + Ot('=') + Ot('[') + Ot(',')
        after = Ot(',') + Ot(']')
        unnecessary = before + after
        group_name = action_str = S(Ot("'")) + S(Ot('"')) + pp.Word(pp.alphas, pp.alphanums + '_') + S(Ot("'")) + S(Ot('"'))
        single_command_str = S(before) + action_str + S(after)
        tuple_command_str = S(before) + S('(') + group_name + S(',') + action_str + S(')') + S(after)
        reader = open(action_list_file)
        self.action_list = []
        for line in reader:
            print(line)
            try:
                group, action = tuple_command_str.parseString(line)
                print("(,)", group, action)
                self.action_list.append((group, action))
                continue
            except pp.ParseException:
                pass
            try:
                command = single_command_str.parseString(line)
                print(" __ ", command)
                self.action_list.append(command[0])
                continue
            except pp.ParseException:
                pass
            try:
                unnecessary.parseString(line)
                continue
            except pp.ParseException:
                pass
            if line:
                print('add_action_list_from_file(' + action_list_file + '): '
                      'can not understand "' + line + '"')
        print(self.action_list)


    def _register_action_groups(self):
        """ makes methods accessable for the action_list """
        reserved_words = ['build_agents', 'run', 'ask_agent',
                'ask_each_agent_in', 'register_action_groups']
        for method in inspect.getmembers(self):
            if (inspect.ismethod(method[1]) and method[0][0] != '_'
                    and method[0] not in reserved_words):
                self._action_groups[method[0]] = method[1]
        self._action_groups['_advance_round'] = self._advance_round

    def declare_resource(self, resource, productivity, product, command='default_resource', group='all'):
        """ every resource you declare here produces productivity units of the
        product per round. For example, 'gold_mine' produces productivity units
        of 'gold', 'land' produces productivity units of 'harvest' and
        'labor_endowment' produces productivity units of 'labor'. By default the
        resource is replentished at the begin of the round. You can change this.
        Insert the command string you chose it self.action_list. One command can
        be associated with several resources.

        resources can be goupe specific, that means that when somebody except
        this group holds them they do not produce. The default is all and its
        better to keep the default 'all' except you have a very good reason to
        do so or if your model is running and you are optimizing. We recommend
        not to optimize before the simulation is working perfectly.
        """
        productivity = str(productivity)
        if command not in self._resource_commands:
            self._resource_commands[command] = []

        if command in self._resource_command_group:
            if self._resource_command_group[command] != group:
                raise SystemExit('Different groups assigned to the same command')
        else:
            self._resource_command_group[command] = group
        self._resource_commands[command].append([resource, productivity, product])

    def _make_resource_command(self, command):
        resources_in_this_command = self._resource_commands[command][:]
        group = self._resource_command_group[command]
        group_and_method = [group, '_produce_resource_rent_and_labor']
        def send_resource_command():
            for productivity in resources_in_this_command:
                self.commands.send_multipart(group_and_method + productivity)
                self._add_agents_to_wait_for(self.num_agents_in_group[group])
        return send_resource_command
        #TODO could be made much faster by sending all resource simultaneously
        #as in _make_perish_command

    def declare_perishable(self, good, command='perish_at_the_round_end'):
        """ This good only lasts one round and than disappers. For example
        labor, if the labor is not used today todays labor is lost.
        In combination with resoure this is useful to model labor or capital.

        In the example below a worker has an endowment of labor and capital.
        Every round he can sell his labor service and rent his capital. If
        he does not the labor service for this round and the rent is lost.

        Args::

         good: the good that perishes
         [command: In order to perish at another point in time you can choose
         a commmand and insert that command in the action list.

         Example::

             w.declare_resource(resource='LAB_endowment', productivity=1000, product='LAB')
             w.declare_resource(resource='CAP_endowment', productivity=1000, product='CAP')
             w.declare_perishable(good='LAB')
             w.declare_perishable(good='CAP')

        """
        if command not in self._perish_commands:
            self._perish_commands[command] = []
        self._perish_commands[command].append(good)

    def _make_perish_command(self, command):
        goods = self._perish_commands[command][:]
        def send_perish_command():
            self.commands.send_multipart(['all', '_perish'] + goods)
            self._add_agents_to_wait_for(self.num_agents_in_group['all'])
        return send_perish_command


    #TODO also for other variables
    def panel_db(self, group, variables='goods', typ='FLOAT', command='round_end'):
        """ writes variables of a group of agents into the database, by default
        the db write is at the end of the round. You can also specify a command
        and insert the command you choose in the action_list. If you choose a
        custom command, you can declace a function with the name command that
        returns the variable you want to track. Details are in agent.follow.

        You can use the same command for several groups, that report at the
        same time.


        Args::

            agentgroup: can be either a group or a list of agents
            variables: default='goods' monitors all the goods the agent owns
            you can insert any variable your agent possesses. For
            self.knows_latin you insert 'knows_latin'. If your agent
            has self.technology you can use 'technology['formula']'
            (typ='CHAR(50)'.
            typ: the type of the sql variable (FLOAT, INT, CHAR(length))
            command

        Example::

         w.start_trade_db(group='firm')

         or

         w.start_trade_db(agents_list=[agent_name('firm', 5), agent_name('household', 10))

        """
        if variables != 'goods':
            raise SystemExit('Not implemented')
        if command not in self._db_commands:
            self._db_commands[command] = []
        self._db_commands[command].append([group, variables, typ])
        self._db.add_panel(group, command)

    def _make_db_command(self, command):
        db_in_this_command = self._db_commands[command][:]
        def send_db_command():
            for db_good in db_in_this_command:
                self.commands.send_multipart([group_address(db_good[0]), '_db_haves', command])
                self._add_agents_to_wait_for(self.num_agents_in_group[db_good[0]])
        return send_db_command

    def follow_agent(self, group_name, number):
        """ This logs a particular agents variables after every subround. By
        default the agent's goods are tracked. You can change this by writing a
        custom follow(self) method that returns a dictionary in the agent.
        (details under agent.follow())
        """
        self._db.add_follow(agent_name(group_name, number))
        self.commands.send_multipart([agent_name(group_name, number), '!', 'follow'])

    def run(self):
        """ This runs the simulation """
        self._db.start()
        if not(self.agent_list):
            raise SystemExit('No Agents Created')
        if not(self.action_list) and not(self._action_list):
            raise SystemExit('No action_list declared')
        for action in self.action_list:
            if len(action) == 2 and type(action) is tuple:
                action_name = '_' + action[0] + '|' + action[1]
                self._action_groups[action_name] = self._make_ask_each_agent_in(action)
                self._action_list.append(action_name)
            else:
                self._action_list.append(action)


        for command in self._db_commands:
            self._action_groups[command] = self._make_db_command(command)
            if command not in self._action_list:
                self._action_list.append(command)

        for command in self._resource_commands:
            self._action_groups[command] = self._make_resource_command(command)
            if command not in self._action_list:
                self._action_list.insert(0, command)

        for command in self._perish_commands:
            self._action_groups[command] = self._make_perish_command(command)
            if command not in self._action_list:
                self._action_list.append(command)

        self._action_list.insert(0, '_advance_round')

        if self._db_follow_agent:
            self._db_follow_agent.start()
        self._write_description_file()
        self._displaydescribtion()
        self._add_agents_to_wait_for(self.num_agents)
        self._wait_for_agents()
        start_time = time.time()
        for year in xrange(self.parameter['number_of_rounds']):
            print("\nRound" + str("%3d" % year))
            for action in self._action_list:
                self._action_groups[action]()
                self._wait_for_agents_than_signal_end_of_comm()
                self.ask_each_agent_in('all', '_end_of_subround_clearing')
                self._wait_for_agents()

        #TODO actions that have no interaction need to signal in order to skip communication step

        print(str("%6.2f" % (time.time() - start_time)))
        self.commands.send_multipart(["all", "!", "die"])
        for agent in list(itertools.chain(*self.agent_list.values())):
            while agent.is_alive():
                time.sleep(0.1)
        self.communication_channel.send("db_agent:close")
        while self._db.is_alive():
            time.sleep(0.05)
        abce_db.convert_to_csv(self.parameter['_path'], 'database')


    def _make_ask_each_agent_in(self, action):
        group_address_var = group_address(action[0])
        number = self.num_agents_in_group[action[0]]
        def ask_each_agent_with_address():
            self._add_agents_to_wait_for(number)
            self.commands.send_multipart([group_address_var, action[1]])
        return ask_each_agent_with_address

    def ask_each_agent_in(self, group_name, command):
        """ This is only relevant when you derive your custom world/swarm not
        in start.py
        applying a method to a group of agents group_name, method.

        Args::

         agent_group: using group_address('group_name', number)
         method: as string

        """
        self._add_agents_to_wait_for(self.num_agents_in_group[group_name])
        self.commands.send_multipart([group_address(group_name), command])

    def ask_agent(self, agent, command):
        """ This is only relevant when you derive your custom world/swarm not
        in start.py
        applying a method to a single agent

        Args::

         agent_name as string or using agent_name('group_name', number)
         method: as string
        """
        self._add_agents_to_wait_for(1)
        self.commands.send_multipart([agent, command])

    def build_agents(self, AgentClass,  number=None, group_name=None, agents_parameters=None):
        """ This method creates agents, the first parameter is the agent class.
        "number_of_agent_class" (e.G. "number_of_firm") should be difined in
        world_parameters.csv. Alternatively you can also specify number = 1.s

        Args::

         AgentClass: is the name of the AgentClass that you imported
         number (optional): number of agents to be created. or the colum name
         of the row in world_parameters.csv that contains this number. If not
         specified the colum name is assumed to be 'number_of_' + agent_name
         (all lowercase). For example number_of_firm, if the class is called
         Firm or name = Firm.
         [group_name (optional): to give the group a different name than the
         class_name. (do not use this if you have not a specific reason]

        Example::

         w.build_agents(Firm, number='number_of_firms')
         # 'number_of_firms' is a column in world_parameters.csv
         w.build_agents(Bank, 1)
         w.build_agents(CentralBank, number=1)
        """
        #TODO single agent groups get extra name without number
        #TODO when there is a group with a single agent the ask_agent has a confusingname
        if not(group_name):
            group_name = AgentClass.__name__
        if number and not(agents_parameters):
            try:
                num_agents_this_group = int(number)
            except ValueError:
                try:
                    num_agents_this_group = self.parameter[number]
                except KeyError:
                    print('build_agents ' + group_name + ': ' + number +
                    ' is not a number or a column name in world_parameters.csv'
                    'or the parameterfile you choose')
        elif not(number) and not(agents_parameters):
            try:
                num_agents_this_group = self.parameter['number_of_' + group_name.lower()]
            except KeyError:
                raise SystemExit('number_of_' + group_name + ' is not in world_parameters.csv')
        elif not(number) and agents_parameters:
            num_agents_this_group = len(agents_parameters)
            self.parameter['number_of_' + group_name.lower()] = num_agents_this_group
        else:
            raise SystemExit('build_agents ' + group_name + ': Either '
                'number_or_parameter_column or agents_parameters must be'
                'specied, NOT both.')
        if not(agents_parameters):
            agents_parameters = [None for _ in range(num_agents_this_group)]

        self.num_agents += num_agents_this_group
        self.num_agents_in_group[group_name] = num_agents_this_group
        self.num_agents_in_group['all'] = self.num_agents
        self.agent_list[group_name] = []
        for idn in range(num_agents_this_group):
            agent = AgentClass(self.parameter, agents_parameters[idn], [idn, group_name, self.__command_addresse])
            agent.name = agent_name(group_name, idn)
            agent.start()
            self.agent_list[group_name].append(agent)


    def build_agents_from_file(self, AgentClass, parameter_file=None, multiply=1, delimiter='\t', quotechar='"'):
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
            def __init__(self, world_parameter, own_parameters, _pass_to_engine):
                AgentEngine.__init__(self, *_pass_to_engine)
                self.size = own_parameters['firm_size']
        """
        if parameter_file == None:
            try:
                parameter_file = self.parameter['agent_parameter_file']
            except KeyError:
                parameter_file = 'agents_parameters.csv'
        agent_class = AgentClass.__name__
        agents_parameters = []
        agent_file = csv.reader(open(parameter_file), delimiter=delimiter, quotechar=quotechar)
        keys = [key for key in agent_file.next()]
        if not('agent_class' in keys):
            keys[0] = 'agent_class'
        for line in agent_file:
            cells = [_number_or_string(cell) for cell in line]
            agent = dict(zip(keys, cells))
            if agent['agent_class'] == agent_class:
                agents_parameters.extend([agent for _ in range(agent.get('number', 1) * multiply)])

        self.build_agents(AgentClass, agents_parameters=agents_parameters)









    def _advance_round(self):
        """ advances round by 1 """
        self.communication_channel.send('db_agent:advance_round')
        self.ask_each_agent_in('all', '_advance_round')

    def _add_agents_to_wait_for(self, number):
        self.communication_channel.send_multipart(['!', '+', str(number)])

    def _wait_for_agents_than_signal_end_of_comm(self):
        self.communication_channel.send_multipart(['!', '}'])
        self.ready.recv()

    def _wait_for_agents(self):
        self.communication_channel.send_multipart(['!', ')'])
        self.ready.recv()

    def _write_description_file(self):
        description = open(
                os.path.abspath(self.parameter['_path'] + '/description.txt'), 'w')
        description.write('Path: ' + str(self.parameter['_path']))
        description.write('\n')
        description.write('\n')
        for key in self.parameter:
            description.write(key + ": " + str(self.parameter[key]) + '\n')

    def _displaydescribtion(self):
        os.system('cls' if os.name=='nt' else 'clear')
        description = open(self.parameter['_path'] + '/description.txt', 'r')
        print(description.read())


class _Communication(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.daemon = True

    def run(self):
        self.context = zmq.Context()
        self.in_soc = self.context.socket(zmq.PULL)
        self.in_soc.bind("ipc://frontend.ipc")
        self.out = self.context.socket(zmq.PUB)
        self.out.bind("ipc://backend.ipc")
        self.ready = self.context.socket(zmq.PUSH)
        self.ready.bind("ipc://ready.ipc")
        agents_finished, total_number = 0, 0
        total_number_known = False
        while True:
            msg = self.in_soc.recv_multipart()
            if msg[0] == '!':
                if msg[1] == '.':
                    agents_finished += 1
                elif msg[1] == '+':
                    total_number += int(msg[2])
                    continue
                elif msg[1] == '}':
                    total_number_known = True
                    send_end_of_communication_sign = True
                elif msg[1] == ')':
                    total_number_known = True
                    send_end_of_communication_sign = False
                if total_number_known:
                    if agents_finished == total_number:
                        agents_finished, total_number = 0, 0
                        total_number_known = False
                        self.ready.send('.')
                        if send_end_of_communication_sign:
                            self.out.send('all.')
            else:
                self.out.send_multipart(msg)




def _number_or_string(word):
    """ returns a int if possible otherwise a float from a string
    """
    try:
        floating_number = float(word)
    except ValueError:
        return word
    try:
        integer = int(word)
    except ValueError:
        return floating_number
    if integer == floating_number:
        return integer
    else:
        return floating_number
