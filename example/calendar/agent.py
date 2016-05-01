from __future__ import division
import abce
from abce import NotEnoughGoods


class Agent(abce.Agent):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        pass

    def wednessday(self):
        print 'wednessday'

    def first(self):
        print 'first'

    def newyearseve(self):
        print 'newyearseve'

    def firstfriday(self):
        print 'drinks in museum'

    def fiveteens(self):
        print 'fiveteens'

    def everythreedays(self):
        print('            ', self.date(), self.date().weekday())
