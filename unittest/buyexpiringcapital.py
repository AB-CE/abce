from __future__ import division
from __future__ import print_function
import abce
from abce.agents import Firm


class BuyExpiringCapital(abce.Agent, Firm):
    def init(self, simulation_parameters, _,):
        self.last_round = simulation_parameters['rounds'] - 1

    def one(self):
        if self.id == 0:
            self.create('money', 10)
            self.buy('buyexpiringcapital', 1,
                     good='xcapital', quantity=10, price=1)
            assert self.possession('xcapital') == 0
            assert self.possession('money') == 0

    def two(self):
        if self.id == 1:
            self.create('xcapital', 10)
            assert self.possession('xcapital') == 10
            assert self.possession('money') == 0
            offer = self.get_offers('xcapital')[0]
            self.possession('xcapital') == 10
            self.accept(offer)
            assert self.possession('xcapital') == 0
            assert self.possession('money') == 10

    def three(self):
        if self.id == 0:
            assert self.possession('xcapital') == 10
            self.destroy('xcapital', 10)
        elif self.id == 1:
            assert self.possession('money') == 10
            self.destroy('money', 10)

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print("BuyExpiringCapital \tOK")
