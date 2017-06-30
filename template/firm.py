from __future__ import division
import abce


class Firm(abce.Agent, abce.Firm, abce.Trade):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.num_households = simulation_parameters['households']
        self.num_firms = simulation_parameters['firms']
