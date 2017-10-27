from abce.agent import Agent
from random import shuffle


class MyAgent(Agent):
    def init(self, simulation_parameters, agent_parameters):
        # print("m", self.idn)
        pass

    def compute(self):
        # print('here', self.idn)
        ll = list(range(1))
        shuffle(ll)
        max(ll)

    def g(self):
        self.accept(self.get_offers('cookie')[0])
        # print(self.possession('cookie'))
