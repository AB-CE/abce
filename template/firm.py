from __future__ import division
import abce
from abce.tools import is_zero, is_positive, is_negative, NotEnoughGoods


class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
