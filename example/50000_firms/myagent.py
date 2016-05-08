from abce.agent import Agent
from random import shuffle


class MyAgent(Agent):
    def init(self, simulation_parameters, agent_parameters):
        #print("m", self.id)
        pass

    def compute(self):
        #print('here', self.id)
        l = range(1)
        shuffle(l)
        max(l)

    def g(self):
        self.accept(self.get_offers('cookie')[0])
        #print(self.possession('cookie'))
