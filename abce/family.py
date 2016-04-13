from collections import defaultdict
import traceback


class Family:
    def __init__(self, Agent, num_agents_this_group, num_managers, batch, agent_args):
        self.agents = []
        self.batch = batch
        self.group = agent_args['group']
        for i in xrange(batch, num_agents_this_group, num_managers):
            self.agents.append(Agent(idn=i, **agent_args))

    def execute(self, command, messages):
        out = defaultdict(list)
        messages = sortmessages(messages)
        for agent in self.agents:
            for message in agent.execute(command, messages[agent.idn]):
                out[(message[0], message[1] % 4)].append(message)
        return out

    def name(self):
        return (self.group, self.batch)

    def execute_internal(self, command):
        for agent in self.agents:
            getattr(agent, command)()

    def declare_expiring(self, good, duration):
        for agent in self.agents:
            agent.declare_expiring(good, duration)

    def init(self, simulation_parameters, agent_parameters):
        for agent in self.agents:
            agent.init(simulation_parameters, agent_parameters)

    def register_perish(self, good):
        for agent in self.agents:
            agent.register_perish(good)

    def register_resource(self, resource, units, product):
        for agent in self.agents:
            agent.register_resource(resource, units, product)

    def register_panel(self, possessins_to_track_panel, variables_to_track_panel):
        for agent in self.agents:
            agent.register_panel(possessins_to_track_panel, variables_to_track_panel)

    def register_aggregate(self, possessins_to_track_panel, variables_to_track_panel):
        for agent in self.agents:
            agent.register_aggregate(possessins_to_track_panel, variables_to_track_panel)

    def set_network_drawing_frequency(self, _network_drawing_frequency):
        for agent in self.agents:
            agent.set_network_drawing_frequency(_network_drawing_frequency)

    def repr(self):
        return "%s: %i - %i" % (self.group, self.agents[0].idn, self.agents[-1].idn)



def sortmessages(new_messages):
    messagess = defaultdict(list)
    for message in new_messages:
        messagess[message[1]].append(message[2])
    return messagess
