from __future__ import division
from __future__ import print_function
import abcEconomics
from abcEconomics.agents import Firm


class ExpiringCapital(abcEconomics.Agent, Firm):
    def init(self, rounds, xcapital):
        self.last_round = rounds - 1
        self.create('xcapital', 1)
        print('============', xcapital)

    def one(self):
        pass

    def two(self):
        pass

    def three(self):
        pass

    def go(self):

        if self.round == 2:
            self.create('xcapital', 10)

        if self.round == 0:
            assert self['xcapital'] == 1
        if self.round == 1:
            assert self['xcapital'] == 1
        if self.round == 2:
            assert self['xcapital'] == 11
        if self.round == 3:
            assert self['xcapital'] == 11
        if self.round == 4:
            assert self['xcapital'] == 11
        if self.round == 5:
            assert self['xcapital'] == 10

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print("simple ExpiringCapital \tOK")
