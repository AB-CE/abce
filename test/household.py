from __future__ import division
import abce
from abce.tools import NotEnoughGoods


class Household(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.create('shares', 1)

    def buying(self):
        print 'buying('
        offers = self.get_offers('corn')
        print offers
        print "(%i)" % len(offers)
        for offer in offers:
            try:
                self.accept(offer)
            except NotEnoughGoods:
                self.reject(offer)
        print 'buying)'

    def checking(self):
        print '------------------ money %i, corn %i' % (self.possession('money'), self.possession('corn'))
