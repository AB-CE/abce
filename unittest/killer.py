import abce


class Killer(abce.Agent, abce.Household):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def kill_silent(self):
        return self.round

    def kill_loud(self):
        return self.round
