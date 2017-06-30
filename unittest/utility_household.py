from __future__ import division
from __future__ import print_function
import abce
from tools import *


class UtilityHousehold(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        self.last_round = simulation_parameters['rounds'] - 1

        if self.id == 0 or self.id == 2:
            def utility(goods):
                return max(goods['a'] ** 0.2, goods['b'] ** 0.5 * goods['c'] ** 0.3)

            use = {'a': 1, 'b': 0.1, 'c': 0}

            self.set_utility_function(utility, use)

        elif self.id == 1 or self.id == 3:
            self.set_cobb_douglas_utility_function(
                {'a': 0.2, 'b': 0.5, 'c': 0.3})

    def one(self):
        pass

    def two(self):
        pass

    def three(self):
        pass

    def clean_up(self):
        pass

    def consumption(self):
        if self.id == 0:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume({'a': 5, 'b': 3, 'c': 1})
            assert utility == max(5 ** 0.2, 3 ** 0.5 * 1 ** 0.3), utility
            assert self.possession('a') == 5
            assert self.possession('b') == 9.7
            assert self.possession('c') == 10
            self.destroy('a')
            self.destroy('b')
            self.destroy('c')

        elif self.id == 1:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume({'a': 5, 'b': 3, 'c': 1})
            assert utility == 5 ** 0.2 * 3 ** 0.5 * 1 ** 0.3, utility
            assert self.possession('a') == 5
            assert self.possession('b') == 7
            assert self.possession('c') == 9
            self.consume_everything()
            assert self.possession('a') == 0
            assert self.possession('b') == 0
            assert self.possession('c') == 0

            pu = self.predict_utility({'a': 5, 'b': 300, 'c': 10})
            assert pu == 5 ** 0.2 * 300 ** 0.5 * 10 ** 0.3

        elif self.id == 2:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume_everything()
            assert is_zero(utility - max(10 ** 0.2, 10 ** 0.5 * 10 ** 0.3)
                           ), (utility, max(10 ** 0.2, 10 ** 0.5 * 10 ** 0.3))
            assert self.possession('a') == 0
            assert self.possession('b') == 9
            assert self.possession('c') == 10
            self.destroy('a')
            self.destroy('b')
            self.destroy('c')

        elif self.id == 3:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume_everything()
            assert is_zero(utility - 10 ** 0.2 * 10 ** 0.5 * 10 **
                           0.3), (utility, 10 ** 0.2 * 10 ** 0.5 * 10 ** 0.3)
            assert self.possession('a') == 0
            assert self.possession('b') == 0
            assert self.possession('c') == 0

            pu = self.predict_utility({'a': 5, 'b': 300, 'c': 10})
            assert pu == 5 ** 0.2 * 300 ** 0.5 * 10 ** 0.3

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print('Test consume:                             \tOK')
            print('Test set_utility_function:                \tOK')
            print('Test set_cobb_douglas_utility_function    \tOK')
