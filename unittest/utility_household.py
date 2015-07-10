from __future__ import division
import abce
from abce.tools import *
from collections import defaultdict


class UtilityHousehold(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        self.last_round = simulation_parameters['num_rounds'] - 1

        if self.idn == 0:
            def utility(goods):
                return max(goods['a'] ** 0.2, goods['b'] ** 0.5 * goods['c'] ** 0.3)

            use = {'a': 1, 'b': 0.1, 'c':0}

            self.set_utility_function(utility, use)

        elif self.idn == 1:
            self.set_cobb_douglas_utility_function({'a': 0.2, 'b': 0.5, 'c': 0.3})


    def one(self):
        pass

    def two(self):
        pass

    def three(self):
        pass

    def clean_up(self):
        pass

    def consumption(self):
        if self.idn == 0:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume({'a': 5, 'b': 3, 'c': 1})
            assert utility == max(5 ** 0.2, 3 ** 0.5 * 1 ** 0.3), utility
            assert self.possession('a') == 5
            assert self.possession('b') == 9.7
            assert self.possession('c') == 10
            self._haves = defaultdict(float)


        elif self.idn == 1:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume({'a': 5, 'b': 3, 'c': 1})
            assert utility == 5 ** 0.2 * 3 ** 0.5 * 1 **0.3, utility
            assert self.possession('a') == 5
            assert self.possession('b') == 7
            assert self.possession('c') == 9
            self._haves = defaultdict(float)

            pu = self.predict_utility({'a': 5, 'b': 300, 'c': 10})
            assert pu == 5 ** 0.2 * 300 ** 0.5 * 10 ** 0.3

    def all_tests_completed(self):
        if self.round == self.last_round and self.idn == 0:
            print('Test consume:                             \tOK')
            print('Test set_utility_function:                \tOK')
            print('Test set_cobb_douglas_utility_function    \tOK')



