from __future__ import division
import abce


class Killer(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        pass

    def kill(self):
        self.delete_agent('victim', self.round, quite=True)
        self.delete_agent('loudvictim', self.round, quite=False)

    def send_message(self):
        if self.round > 0:
            self.send(('victim', self.round - 1), 'topic', 'creepy hello')
