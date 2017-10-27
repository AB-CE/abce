from abce.agent import Agent
from random import shuffle


class MyAgent(Agent):
    def init(self, simulation_parameters, agent_parameters):
        print("init", self.id)

    def compute(self):
        # print('here', self.idn)
        return None
        ll = list(range(10000))
        shuffle(ll)
        max(ll)
