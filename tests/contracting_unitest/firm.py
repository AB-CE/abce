from __future__ import division
import abce


class Firm(abce.Agent, abce.Firm, abce.Contracting):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.num_households = simulation_parameters['households']
        self.num_firms = simulation_parameters['firms']

    def one(self):
        if self.round % 10 == 0:
            self.request_contract()
