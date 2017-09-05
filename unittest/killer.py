from __future__ import division
import abce


class Killer(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        pass

    def kill_silent(self):
        return (('victim', self.round), True)

    def kill_loud(self):
        return (('loudvictim', self.round), False)

    def send_message(self):
        if self.round > 0:
            self.send(('victim', self.round - 1), 'topic', 'creepy hello')
