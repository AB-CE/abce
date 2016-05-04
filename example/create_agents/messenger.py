from __future__ import division
import abce
from abce import NotEnoughGoods


class Messenger(abce.Agent):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.count = 1

    def messaging(self):
        max_firm = 2 ** self.round
        for id in range(max_firm):
            self.message('firm', id, 'msg', id)

        max_hh = 2 ** self.round
        for id in range(max_hh):
            self.message('household', id, 'msg', id)
