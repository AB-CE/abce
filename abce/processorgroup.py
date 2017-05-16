from builtins import range
from builtins import object
from builtins import list
from builtins import dict
from collections import defaultdict
from pprint import pprint
import traceback
import time
import random


class ProcessorGroup(object):
    def __init__(self, num_managers, batch):
        self.agents = {}
        self.batch = batch
        self.num_managers = num_managers
        self.pigeonboxes = {}
        self.mymessages = list()

    def add_group(self, Agent, num_agents_this_group, agent_args, parameters, agent_parameters, agent_params_from_sim):
        group = agent_args['group']
        self.agents[group] = []
        self.apfs = agent_params_from_sim
        for i in range(self.batch, num_agents_this_group, self.num_managers):
            agent = self.make_an_agent(Agent, id=i, agent_args=agent_args, parameters=parameters, agent_parameters=agent_parameters[i])
            self.agents[group].append(agent)

        self.pigeonboxes[group] = list(list() for _ in range(len(self.agents[group])))

    def append(self, Agent, id, agent_args, parameters, agent_parameters):
        group = agent_args['group']
        agent = self.make_an_agent(Agent, id, agent_args, parameters, agent_parameters)
        self.agents[group].append(agent)
        self.pigeonboxes[group].append([])

    def make_an_agent(self, Agent, id, agent_args, parameters, agent_parameters):
        agent_args['num_managers'] = self.num_managers
        agent = Agent(id=id, **agent_args)
        try:
            agent.init(parameters, agent_parameters)
        except AttributeError:
                if 'init' not in dir(agent):
                    print("Warning: agent %s has no init function" % agent.group)
                else:
                    raise
        except KeyboardInterrupt:
            return None
        except:
            time.sleep(random.random())
            traceback.print_exc()
            raise SystemExit()
        for good, duration in self.apfs['expiring']:
            agent._declare_expiring(good, duration)
        for good in self.apfs['perishable']:
            agent._register_perish(good)
        for resource, units, product in self.apfs['resource_endowment']:
            agent._register_resource(resource, units, product)
        agent._register_panel(*self.apfs['panel'])
        agent._register_aggregate(*self.apfs['aggregate'])
        agent._set_network_drawing_frequency(self.apfs['ndf'])
        return agent


    def execute(self, groups, command, messages):
        try:
            out = [[] for _ in range(self.num_managers + 1)]
            self.put_messages_in_pigeonbox(messages)
            for group in groups:
                for i, agent in enumerate(self.agents[group]):
                    outmessages = agent._execute(command, self.pigeonboxes[group][i])
                    for pgid, msg in enumerate(outmessages):
                        if pgid == self.batch:
                            self.mymessages.extend(msg)
                        else:
                            out[pgid].extend(msg)
                self.pigeonboxes[group] = list(list() for _ in range(len(self.agents[group])))
        except:
            traceback.print_exc()
            raise
        return out


    def replace_with_dead(self, group, id, DeadAgent):
        """ replaces a deleted agent """
        self.agents[group][id // self.num_managers] = DeadAgent()

    def name(self):
        return (self.group, self.batch)

    def execute_internal(self, command):
        for group in self.agents.values():
            for agent in group:
                try:
                    getattr(agent, command)()
                except KeyboardInterrupt:
                    return None
                except:
                    time.sleep(random.random())
                    traceback.print_exc()
                    raise SystemExit()

    def put_messages_in_pigeonbox(self, new_messages):
        for group, id, message in new_messages:
            self.pigeonboxes[group][id // self.num_managers].append(message)
        for group, id, message in self.mymessages:
            self.pigeonboxes[group][id // self.num_managers].append(message)
        self.mymessages.clear()


    def len(self):
        return sum([len(group) for group in self.agents.values()])

    def repr(self):
        return str(self.batch)

    def __repr__(self):
        return repr()


def defaultdict_list():
    return defaultdict(list)
