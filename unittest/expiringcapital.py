from __future__ import division
import random
from abce.tools import NotEnoughGoods, is_zero
import abce


class ExpiringCapital(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, _,):
        self.last_round = simulation_parameters['num_rounds'] - 1
        self.create('xcapital', 1)
        print '============', self.simulation_parameters['xcapital']

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
            assert self.possession('xcapital') == 1
        if self.round == 1:
            assert self.possession('xcapital') == 1
        if self.round == 2:
            assert self.possession('xcapital') == 11
        if self.round == 3:
            assert self.possession('xcapital') == 11
        if self.round == 4:
            assert self.possession('xcapital') == 11
        if self.round == 5:
            assert self.possession('xcapital') == 10

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.idn == 0:
            print("simple ExpiringCapital \tOK")
