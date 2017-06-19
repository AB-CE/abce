from abce.agent import Agent
from random import shuffle


class MyAgent(Agent):
    def init(self, simulation_parameters, agent_parameters):
        print("init", self.idn)

    def compute(self):
        #print('here', self.idn)
        return None
        l = range(10000)
        shuffle(l)
        max(l)
