from collections import defaultdict
from abce.deadagent import DeadAgent
import traceback
import time
import random


class Family:
    def __init__(self, Agent, num_agents_this_group, num_managers, batch, agent_args):
        self.agents = []
        self.batch = batch
        self.group = agent_args['group']
        self.num_managers = num_managers
        for i in xrange(batch, num_agents_this_group, num_managers):
            self.agents.append(Agent(id=i, **agent_args))

    def append(self, Agent, id, agent_args):
            self.agents.append(Agent(id=id, **agent_args))

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

    def declare_expiring(self, good, duration):
        for agent in self.agents:
            agent._declare_expiring(good, duration)

    def init(self, simulation_parameters, agent_parameters):
        for agent in self.agents:
            try:
                agent.init(simulation_parameters, agent_parameters[agent.id])
            except KeyboardInterrupt:
                return None
            except:
                time.sleep(random.random())
                traceback.print_exc()
                raise SystemExit()

    def register_perish(self, good):
        for agent in self.agents:
            agent._register_perish(good)

    def register_resource(self, resource, units, product):
        for agent in self.agents:
            agent._register_resource(resource, units, product)

    def register_panel(self, possessins_to_track_panel, variables_to_track_panel):
        for agent in self.agents:
            agent._register_panel(possessins_to_track_panel, variables_to_track_panel)

    def register_aggregate(self, possessins_to_track_panel, variables_to_track_panel):
        for agent in self.agents:
            agent._register_aggregate(possessins_to_track_panel, variables_to_track_panel)

    def set_network_drawing_frequency(self, _network_drawing_frequency):
        for agent in self.agents:
            agent._set_network_drawing_frequency(_network_drawing_frequency)

    def last_added_agent(self, command, parameters):
        getattr(self.agents[-1], command)(*parameters)

    def repr(self):
        return "%s: %i - %i" % (self.group, self.agents[0].id, self.agents[-1].id)



def sortmessages(new_messages):
    messagess = defaultdict(list)
    for message in new_messages:
        messagess[message[1]].append(message[2])
    return messagess
