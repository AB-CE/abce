from builtins import range
from abce.agent import Agent
from random import shuffle


class YourAgent(Agent):
    def init(self, simulation_parameters, agent_parameters):
        #print("y", self.id)
        pass

    def compute(self):
        #print('here', self.id)
        l = list(range(1))
        shuffle(l)
        max(l)

    def s(self):
        self.create('cookie', 1)
        self.sell('myagent', self.id, good='cookie', price=0, quantity=1)
        assert self.possession('cookie') == 0
