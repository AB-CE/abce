from __future__ import division
import abce


class Killer(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        pass

    def kill_silent(self):
        return ('victim', self.round)

    def kill_loud(self):
        return ('loudvictim', self.round)
