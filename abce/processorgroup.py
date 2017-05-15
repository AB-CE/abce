from builtins import range
from builtins import object
from collections import defaultdict
from abce.deadagent import DeadAgent
from pprint import pprint
import traceback
import time
import random


class ProcessorGroup(object):
    def __init__(self, num_managers, batch):
        self.agents = {}
        self.batch = batch
        self.num_managers = num_managers

    def add_group(self, Agent, num_agents_this_group, agent_args, parameters, agent_parameters, agent_params_from_sim):
        group = agent_args['group']
        self.agents[group] = []
        self.apfs = agent_params_from_sim
        for i in range(self.batch, num_agents_this_group, self.num_managers):
            agent = self.make_an_agent(Agent, id=i, agent_args=agent_args, parameters=parameters, agent_parameters=agent_parameters[i])
            self.agents[group].append(agent)

    def append(self, Agent, id, agent_args, parameters, agent_parameters):
        group = agent_args['group']
        agent = self.make_an_agent(Agent, id, agent_args, parameters, agent_parameters)
        self.agents[group].append(agent)

    def make_an_agent(self, Agent, id, agent_args, parameters, agent_parameters):
        agent = Agent(id=id, **agent_args, num_managers=self.num_managers)
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
            out = defaultdict(list)
            for group in groups:
                group_messages = sortmessages(messages[group])
                for i, agent in enumerate(self.agents[group]):
                    outmessages = agent._execute(command, group_messages[i * self.num_managers + self.batch])
                    for (pgid, group), msg in outmessages.items():
                        out[(pgid, group)].extend(msg)
        except:
            traceback.print_exc()
            raise
        return out

    def remove(self, group, ids):
        """ removes a deleted agent, agents that are removed, don't read their
        messages, if they get a message the simulation stops """
        self.agents[group] = [agent for agent in self.agents[group] if agent.id not in ids]

    def replace_with_dead(self, group, ids):
        """ replaces a deleted agent, so that all messages the agent receives
        are deleted. The agent is inactive"""
        for i in range(len(self.agents)):
            if self.agents[group][i].id in ids:
                self.agents[group][i] = DeadAgent()

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

    def len(self):
        return sum([len(group) for group in self.agents.values()])

    def repr(self):
        return str(self.batch)

    def __repr__(self):
        return repr()

def sortmessages(new_messages):
    messagess = defaultdict(list)
    for message in new_messages:
        messagess[message[0]].append(message[1])
    return messagess

def defaultdict_list():
    return defaultdict(list)
