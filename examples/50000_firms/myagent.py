from builtins import range
from abce.agent import Agent
from random import shuffle


class MyAgent(Agent):
    def init(self, simulation_parameters, agent_parameters):
        #print("m", self.id)
        pass

    def compute(self):
        #print('here', self.id)
        l = list(range(1))
        shuffle(l)
        max(l)

    def g(self):
        for offer in self.get_offers('cookie'):
            self.accept(offer)
        # print(self.possession('cookie'))
