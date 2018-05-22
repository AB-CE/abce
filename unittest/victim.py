import abce
from abce.agents import Household


class Victim(abce.Agent, Household):
    def init(self):
        self.count = 1

    def am_I_dead(self):
        if self.id < self.round:
            raise Exception("should be dead %i" % self.id)
