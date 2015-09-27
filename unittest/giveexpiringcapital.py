from __future__ import division
import abce
from abce.firm import Firm


class GiveExpiringCapital(abce.Agent, Firm):
    def init(self, simulation_parameters, _,):
        self.last_round = simulation_parameters['num_rounds'] - 1
        if self.idn == 0:
            self.create('xcapital', 10)
            assert self.possession('xcapital') == 10, self.possession('xcapital')

    def one(self):
        if self.idn == 0:
            assert self.possession('xcapital') == 10, self.possession('xcapital')
            self.give('giveexpiringcapital', 1, 'xcapital', 10)
            assert self.possession('xcapital') == 0, self.possession('xcapital')

    def two(self):
        if self.idn == 1:
            assert self.possession('xcapital') == 10, self.possession('xcapital')
            self.give('giveexpiringcapital', 0, 'xcapital', 10)
            assert self.possession('xcapital') == 0, self.possession('xcapital')

    def three(self):
        pass

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.idn == 0:
            print("Give ExpiringCapital \tOK")
