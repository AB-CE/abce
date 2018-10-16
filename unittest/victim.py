import abcEconomics
from abcEconomics.agents import Household


class Victim(abcEconomics.Agent, Household):
    def init(self):
        self.count = 1

    def am_I_dead(self):
        if self.id < self.time:
            raise Exception("should be dead %i" % self.id)
