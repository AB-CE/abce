from __future__ import division
import abce
from abce.firm import Firm


class BuyExpiringCapital(abce.Agent, Firm):
    def init(self, simulation_parameters, _,):
        self.last_round = simulation_parameters['num_rounds'] - 1

    def one(self):
        if self.idn == 0:
            self.create('money', 10)
            self.buy('buyexpiringcapital', 1, good='xcapital', quantity=10, price=1)
            assert self.possession('xcapital') == 0
            assert self.possession('money') == 0

    def two(self):
        if self.idn == 1:
            self.create('xcapital', 10)
            assert self.possession('xcapital') == 10
            assert self.possession('money') == 0
            offer = self.get_offers('xcapital')[0]
            self.possession('xcapital') == 10
            self.accept(offer)
            assert self.possession('xcapital') == 0
            assert self.possession('money') == 10

    def three(self):
        if self.idn == 0:
            assert self.possession('xcapital') == 10
            self.destroy('xcapital', 10)
        elif self.idn == 1:
            assert self.possession('money') == 10
            self.destroy('money', 10)

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.idn == 0:
            print("BuyExpiringCapital \tOK")
