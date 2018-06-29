from __future__ import division
from __future__ import print_function
import abcEconomics
from abcEconomics.agents import Firm


class Firm(abcEconomics.Agent, Firm):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.create('field', 1)

    def selling(self):
        print('selling(')
        print('money %i, corn %i' % (self.possession('money'), self.possession('corn')))
        #for x in xrange(10000):
        #    x = x * x
        self.checkorders = self.sell('household', self.id, 'corn', 1, 1)
        # for offer in self.given_offers:
        #     try:
        #         print 'out', offer, self.given_offers[offer]['status'], self.given_offers[offer]['status_round'], '.'
        #     except KeyError:
        #         print offer, '--'
        print('selling)')

    def nothing(self):
        print('nothing')
