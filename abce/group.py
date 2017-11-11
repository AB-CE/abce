from collections import deque
import traceback
from time import sleep
import random


def get_methods(a_class):
    return [method for method in a_class.__dict__.keys() if
            callable(getattr(a_class, method)) and not
            method.startswith('_') and method != 'init']


class Group(object):
    def __init__(self, sim, group_name, agent_class=None):
        self.sim = sim
        self.num_managers = sim.processes
        self.group_name = group_name
        self.agent_class = agent_class
        for method in dir(agent_class):
            if method[0] != '_':
                setattr(self, method,
                        eval('lambda self=self, *argc, **kw: self.do("%s", *argc, **kw)' %
                             method))

        self.panel_serial = 0
        self.last_action = "Begin_of_Simulation"
        self.free_ids = deque()

    def __add__(self, g):
        return Group(self.sim, self.groups + g.groups, self.agent_class)

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

    def add_group(self, Agent, num_agents_this_group, agent_args, parameters,
                  agent_parameters, agent_params_from_sim):
        self.agents = []
        self.apfs = agent_params_from_sim
        for i in range(num_agents_this_group):
            agent = self.make_an_agent(Agent, id=i, agent_args=agent_args,
                                       parameters=parameters,
                                       agent_parameters=agent_parameters[i])
            self.agents.append(agent)

    def append(self, Agent, agent_args, parameters, agent_parameters):
        try:
            id = self.free_ids.popleft()
        except IndexError:
            id = len(self.agents)
            self.agents.append(None)
        agent = self.make_an_agent(
            Agent, id, agent_args, parameters, agent_parameters)
        self.agents[id] = agent
        return id

    def make_an_agent(self, Agent, id, agent_args,
                      parameters, agent_parameters):
        agent_args['num_managers'] = self.num_managers
        agent = Agent(id=id, **agent_args)
        for good, duration in self.apfs['expiring']:
            agent._declare_expiring(good, duration)
        for good in self.apfs['perishable']:
            agent._register_perish(good)
        for resource, units, product in self.apfs['resource_endowment']:
            agent._register_resource(resource, units, product)
        try:
            agent.init(parameters, agent_parameters)
        except AttributeError:
            if 'init' not in dir(agent):
                print("Warning: agent %s has no init function" % agent.group)
            else:
                raise
        except KeyboardInterrupt:
            return None
        except Exception:
            sleep(random.random())
            traceback.print_exc()
            raise Exception()
        return agent

    def do(self, command, *args, **kwargs):
        self.last_action = command
        rets = []
        self.put_messages_in_pigeonbox()
        for agent in self.agents:
            try:
                ret = agent._execute(command, args, kwargs)
                rets.append(ret)
            except AttributeError:
                pass
        for agent in self.agents:
            try:
                agent._post_messages(self.sim._groups)
            except AttributeError:
                pass
        return rets

    def delete_agent(self, id):
        self.agents[id] = None
        self.free_ids.append(id)

    def name(self):
        return (self.group, self.batch)

    def execute_advance_round(self, time):
        for agent in self.agents:
            try:
                agent._advance_round(time)
            except KeyboardInterrupt:
                return None
            except AttributeError:
                pass
            except Exception:
                sleep(random.random())
                traceback.print_exc()
                raise Exception()

    def put_messages_in_pigeonbox(self):
        for _, id, msg in self.sim.messagess[self.group_name]:
            self.agents[id].inbox.append(msg)
        self.sim.messagess[self.group_name].clear()

    def len(self):
        """ Returns the length of a group """
        return sum([1 for agent in self.agents if agent is not None])

    def repr(self):
        return str(self.batch)

    def __repr__(self):
        return repr()
