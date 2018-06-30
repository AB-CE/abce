
import abcEconomics
from abcEconomics.agents import Firm


class GiveExpiringCapital(abcEconomics.Agent, Firm):
    def init(self, rounds):
        self.last_round = rounds - 1
        if self.id == 0:
            self.create('xcapital', 10)
            assert self['xcapital'] == 10, self['xcapital']

    def one(self):
        if self.id == 0:
            assert self['xcapital'] == 10, self['xcapital']
            self.give('giveexpiringcapital', 1, 'xcapital', 10)
            assert self['xcapital'] == 0, self['xcapital']

    def two(self):
        if self.id == 1:
            assert self['xcapital'] == 10, self['xcapital']
            self.give('giveexpiringcapital', 0, 'xcapital', 10)
            assert self['xcapital'] == 0, self['xcapital']

    def three(self):
        pass

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print("Give ExpiringCapital \tOK")
