import abcEconomics
from abcEconomics.agents import Household

from tools import is_zero


class UtilityHousehold(abcEconomics.Agent, Household):
    def init(self, rounds):
        self.last_round = rounds - 1

        if self.id == 0 or self.id == 2:
            def utility_function(a, b, c):
                utility = max(a ** 0.2, b ** 0.5 * c ** 0.3)
                a = 0
                b = 0.9 * b
                return utility, locals()

            self.utility_function = utility_function

        elif self.id == 1 or self.id == 3:
            self.utility_function = self.create_cobb_douglas_utility_function(
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
            utility = self.consume(self.utility_function, {'a': 5, 'b': 3, 'c': 1})
            assert utility == max(5 ** 0.2, 3 ** 0.5 * 1 ** 0.3), utility
            assert self['a'] == 5
            assert self['b'] == 9.7
            assert self['c'] == 10
            self.destroy('a')
            self.destroy('b')
            self.destroy('c')

        elif self.id == 1:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume(self.utility_function, {'a': 5, 'b': 3, 'c': 1})
            assert utility == 5 ** 0.2 * 3 ** 0.5 * 1 ** 0.3, utility
            assert self['a'] == 5
            assert self['b'] == 7
            assert self['c'] == 9
            self.consume(self.utility_function, ['a', 'b', 'c'])
            assert self['a'] == 0
            assert self['b'] == 0
            assert self['c'] == 0

            pu = self.utility_function(**{'a': 5, 'b': 300, 'c': 10})
            assert pu == 5 ** 0.2 * 300 ** 0.5 * 10 ** 0.3

        elif self.id == 2:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume(self.utility_function, ['a', 'b', 'c'])
            assert is_zero(utility - max(10 ** 0.2, 10 ** 0.5 * 10 ** 0.3)
                           ), (utility, max(10 ** 0.2, 10 ** 0.5 * 10 ** 0.3))
            assert self['a'] == 0
            assert self['b'] == 9
            assert self['c'] == 10
            self.destroy('a')
            self.destroy('b')
            self.destroy('c')

        elif self.id == 3:
            self.create('a', 10)
            self.create('b', 10)
            self.create('c', 10)
            utility = self.consume(self.utility_function, ['a', 'b', 'c'])
            assert is_zero(utility - 10 ** 0.2 * 10 ** 0.5 * 10 **
                           0.3), (utility, 10 ** 0.2 * 10 ** 0.5 * 10 ** 0.3)
            assert self['a'] == 0
            assert self['b'] == 0
            assert self['c'] == 0

            pu = self.utility_function(**{'a': 5, 'b': 300, 'c': 10})
            assert pu == 5 ** 0.2 * 300 ** 0.5 * 10 ** 0.3

    def all_tests_completed(self):
        if self.time == self.last_round and self.id == 0:
            print('Test consume:                             \tOK')
            print('Test set_utility_function:                \tOK')
            print('Test set_cobb_douglas_utility_function    \tOK')
