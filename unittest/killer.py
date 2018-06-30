import abcEconomics
from abcEconomics.agents import Household


class Killer(abcEconomics.Agent, Household):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def kill_silent(self):
        return ('victim', self.time)

    def kill_loud(self):
        return ('loudvictim', self.time)
