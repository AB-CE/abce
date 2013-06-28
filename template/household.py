from __future__ import division
import abce
from abce.tools import is_zero, is_positive, is_negative, NotEnoughGoods


class Household(abce.Agent, abce.Household):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abce.Agent.__init__(self, *_pass_to_engine)

