from __future__ import division
import abce


class Killer(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        pass

    def kill(self):
        self.delete_agent('Victim', self.round, quite=True)
        self.delete_agent('Loudvictim', self.round, quite=False)

    def send_message(self):
        if self.round > 0:
            self.message('Victim', self.round - 1, 'topic', 'creepy hello')
