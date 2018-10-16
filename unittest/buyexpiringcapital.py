
from __future__ import division
from __future__ import print_function
import abcEconomics
from abcEconomics.agents import Firm


class BuyExpiringCapital(abcEconomics.Agent, Firm):
    def init(self, rounds):
        self.last_round = rounds - 1

    def one(self):
        if self.id == 0:
            self.create('money', 10)
            self.buy('buyexpiringcapital', 1,
                     good='xcapital', quantity=10, price=1)
            assert self.free('xcapital') == 0
            assert self.free('money') == 0

    def two(self):
        if self.id == 1:
            self.create('xcapital', 10)
            assert self['xcapital'] == 10
            assert self['money'] == 0
            offer = self.get_offers('xcapital')[0]
            self['xcapital'] == 10
            self.accept(offer)
            assert self['xcapital'] == 0
            assert self['money'] == 10

    def three(self):
        if self.id == 0:
            assert self['xcapital'] == 10
            self.destroy('xcapital', 10)
        elif self.id == 1:
            assert self['money'] == 10
            self.destroy('money', 10)

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print("BuyExpiringCapital \tOK")
