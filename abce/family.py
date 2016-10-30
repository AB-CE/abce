from builtins import range
from builtins import object
from collections import defaultdict
from abce.deadagent import DeadAgent
import traceback
import time
import random


class Family(object):
    def __init__(self, Agent, num_agents_this_group, num_managers, batch, agent_args, parameters, agent_parameters, agent_params_from_sim):
        self.agents = []
        self.batch = batch
        self.group = agent_args['group']
        self.num_managers = num_managers
        self.apfs = agent_params_from_sim
        for i in xrange(batch, num_agents_this_group, num_managers):
            agent = self.make_an_agent(Agent, id=i, agent_args=agent_args, parameters=parameters, agent_parameters=agent_parameters[i])
            self.agents.append(agent)

    def append(self, Agent, id, agent_args, parameters, agent_parameters):
        agent = self.make_an_agent(Agent, id, agent_args, parameters, agent_parameters)
        self.agents.append(agent)

    def make_an_agent(self, Agent, id, agent_args, parameters, agent_parameters):
        agent = Agent(id=id, **agent_args)
        try:
            agent.init(parameters, agent_parameters)
        except AttributeError:
            print("Warning: agent %s has no init function" % agent.group)
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


    def execute(self, command, messages):
        out = defaultdict(list)
        messages = sortmessages(messages)
        for agent in self.agents:
            for message in agent._execute(command, messages[agent.id]):
                out[(message[0], message[1] % self.num_managers)].append(message)
        return out

    def remove(self, ids):
        """ removes a deleted agent, agents that are removed, don't read their
        messages, if they get a message the simulation stops """
        self.agents = [agent for agent in self.agents if agent.id not in ids]

    def replace_with_dead(self, ids):
        """ replaces a deleted agent, so that all messages the agent receives
        are deleted. The agent is inactive"""
        for i in range(len(self.agents)):
            if self.agents[i].id in ids:
                self.agents[i] = DeadAgent()

    def name(self):
        return (self.group, self.batch)

    def execute_internal(self, command):
        for agent in self.agents:
            try:
                getattr(agent, command)()
            except KeyboardInterrupt:
                return None
            except:
                time.sleep(random.random())
                traceback.print_exc()
                raise SystemExit()

    def repr(self):
        return "%s: %i - %i" % (self.group, self.agents[0].id, self.agents[-1].id)

def sortmessages(new_messages):
    messagess = defaultdict(list)
    for message in new_messages:
        messagess[message[1]].append(message[2])
    return messagess
