from __future__ import division
import abceagent
from abcetools import is_zero, is_positive, is_negative, NotEnoughGoods


class Household(abceagent.Agent, abceagent.Household):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abceagent.Agent.__init__(self, *_pass_to_engine)

