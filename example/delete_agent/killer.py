from __future__ import division
import abce
from abce import NotEnoughGoods


class Killer(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        pass

    def kill(self):
        print 'kill', self.round
        self.delete_agent('agent', self.round, quite=True)
