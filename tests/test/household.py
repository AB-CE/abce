from __future__ import division
from __future__ import print_function
import abcEconomics
from abcEconomics.notenoughgoods import NotEnoughGoods


class Household(abcEconomics.Agent, abcEconomics.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.create('shares', 1)

    def buying(self):
        print('buying(')
        offers = self.get_offers('corn')
        print(offers)
        print("(%i)" % len(offers))
        for offer in offers:
            try:
                self.accept(offer)
            except NotEnoughGoods:
                self.reject(offer)
        print('buying)')

    def checking(self):
        print('------------------ money %i, corn %i' % (self.possession('money'), self.possession('corn')))
