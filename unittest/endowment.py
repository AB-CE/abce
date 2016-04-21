from __future__ import division
import abce
from tools import *


class Endowment(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        self.last_round = simulation_parameters['rounds'] - 1
        self.create('labor_endowment', 1)
        self.create('cow', 1)
        self.set_cobb_douglas_utility_function({'milk': 2})

    def Iconsume(self):
        assert self.possession('labor') == 5, self.possession('labor')
        assert self.possession('milk') == 10 + self.round * (10 - 3), self.possession('milk')
        milk = self.possession('milk')
        utility = self.consume({'milk': 3})
        assert utility == 9, utility
        assert milk - 3 == self.possession('milk'), self.possession('milk')

    def one(self):
        pass

    def two(self):
        pass

    def three(self):
        pass

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.idn == 0:
            print('Test declare_round_endowment:\t\t\tOK')
            print('Test s.declare_perishable:\t\t\tOK')
            # utility testnot exaustive!

