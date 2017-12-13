from __future__ import division
import abce


class Victim(abce.Agent, abce.Household):
    def init(self):
        # your agent initialization goes here, not in __init__
        self.count = 1

    def am_I_dead(self):
        if self.id < self.round:
            raise Exception("should be dead %i" % self.id)
