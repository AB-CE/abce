from __future__ import division  # makes division work correctly
import abce
from abce.tools import is_zero, is_positive, is_negative, NotEnoughGoods


class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        """ 1. Gets an initial amount of money
        2. create a cobb_douglas function: GOOD = 1 * labor ** 1.
        """
        self.create('money', 1)
        self.set_cobb_douglas("GOOD", 1, {"labor": 1})

    def buy_labor(self):
        """ receives the offers and accepts them one by one """
        oo = self.get_offers("labor")
        for offer in oo:
            self.accept(offer)

    def production(self):
        """ uses all labor that is available and produces
        according to the set cobb_douglas function """
        self.produce_use_everything()

    def sell_goods(self):
        """ offers one unit of labor to firm 0, for the price of 1 "money" """
        self.sell('household', 0, "GOOD", self.possession("GOOD"), 1)

