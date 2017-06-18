from __future__ import division  # makes division work correctly
import abce
import random


class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        """ 1. Gets an initial amount of money
        2. create a cobb_douglas function: GOOD = 1 * labor ** 1.
        """
        self.create('money', 1000)
        self.mygood = "GOOD%i" % self.id  # GOOD1 if self.id == 1
        self.set_cobb_douglas(self.mygood, 1, {"labor": 1})
        self.price = random.random() * 2

    def buy_labor(self):
        """ receives all labor offers and accepts them one by one """
        oo = self.get_offers("labor")
        for offer in oo:
            self.accept(offer, min(offer.quantity, self.possession('money')))

    def production(self):
        """ uses all labor that is available and produces
        according to the set cobb_douglas function """
        self.produce_use_everything()

    def quotes(self):
        self.message('household', 0, 'quote', (self.mygood, self.price))

    def sell_goods(self):
        """ offers one unit of labor to firm 0, for the price of 1 "money" """
        oo = self.get_offers(self.mygood)
        for offer in oo:
            self.accept(offer, min(offer.quantity,
                                   self.possession(self.mygood)))

    def adjust_price(self):
        self.inventory = self.possession(self.mygood)
        if self.inventory < 4:
            self.price += random.random() * 0.01  # random number [0, 0.1]
        if self.inventory > 6:
            self.price = max(0.01, self.price - random.random()
                             * 0.01)  # random number [0, 0.1]
