from __future__ import division
import abce


class Killer(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        pass

    def kill(self):
        print 'kill', self.round
        self.delete_agent('agent', self.round, quite=True)

    def send_message(self):
        self.message('agent', self.round - 1, 'topic', 'creepy hello')
