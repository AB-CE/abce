import abcEconomics
from abcEconomics.agents import Firm

from tools import is_zero


class ProductionMultifirm(abcEconomics.Agent, Firm):
    def init(self, rounds):
        self.last_round = rounds - 1

        def production_function(a, b):
            consumption_good = max(a ** 2, a ** 0.5 * b)
            a = 0
            b = b * 0.9
            return locals()

        self.pf = production_function
        self.cd = self.create_cobb_douglas('consumption_good', 5, {'a': 2, 'b': 1})
        self.leontief = self.create_leontief('consumption_good', {'a': 3, 'b': 1})
        self.car = self.create_leontief('car', {'wheels': 4, 'chassi': 1})
        self.ces = self.create_ces('consumption_good', gamma=0.5, shares={
                                   'a': 0.25, 'b': 0.25, 'c': 0.5})
        self.ces_flexible = self.create_ces(
            'consumption_good', gamma=0.5, multiplier=2)

        def many_goods_pf(a, b, c):
            soft_rubber = a ** 0.25 * b ** 0.5 * c ** 0.25
            hard_rubber = a ** 0.1 * b ** 0.2 * c ** 0.01
            waste = b / 2
            a = 0
            b = b * 0.9
            c = c
            return locals()

        self.many_goods_pf = many_goods_pf

    def production(self):
        self.create('a', 2)
        self.create('b', 2)
        self.produce(self.pf, {'a': 1, 'b': 2})

        assert self['a'] == 1, self['a']
        assert self['b'] == 1.8, self['b']
        assert is_zero(self['consumption_good'] - 1. ** 0.5 * 2), \
            self['consumption_good']
        self.destroy('a')
        self.destroy('b')
        self.destroy('consumption_good')

        result = self.pf(**{'a': 10, 'b': 10})
        assert result['consumption_good'] == max(10 ** 2, 10 ** 0.5 * 10)
        assert result['a'] == 0, result['a']
        assert result['b'] == 9, result['b']

        self.create('a', 2)
        self.create('b', 2)
        self.produce(self.cd, {'a': 1, 'b': 2})

        assert self['a'] == 1, self['a']
        assert self['b'] == 0, self['b']
        assert self['consumption_good'] == 5 * \
            1 ** 2 * 2 ** 1, self['consumption_good']
        self.destroy('a')
        self.destroy('b')
        self.destroy('consumption_good')

        self.create('a', 2)
        self.create('b', 2)
        self.produce(self.leontief, {'a': 1, 'b': 2})

        assert self['a'] == 1, self['a']
        assert self['b'] == 0, self['b']
        assert self['consumption_good'] == min(
            1 * 3, 2 * 1), self['consumption_good']
        self.destroy('a')
        self.destroy('consumption_good')

        self.create('a', 10)
        self.create('b', 10)
        self.create('c', 10)
        self.produce(self.many_goods_pf, {'a': 1, 'b': 2, 'c': 5})

        assert self['a'] == 9, self['a']
        assert self['b'] == 9.8, self['b']
        assert self['c'] == 10, self['c']
        assert self['soft_rubber'] == 1 ** 0.25 * \
            2 ** 0.5 * 5 ** 0.25, self['soft_rubber']
        assert self['hard_rubber'] == 1 ** 0.1 * \
            2 ** 0.2 * 5 ** 0.01, self['hard_rubber']
        assert self['waste'] == 2 / 2, self['waste']
        self.destroy('a')
        self.destroy('b')
        self.destroy('c')
        self.destroy('soft_rubber')
        self.destroy('hard_rubber')
        self.destroy('waste')

        self.create('a', 2)
        self.create('b', 2)
        self.create('c', 4)
        self.produce(self.ces, {'a': 1, 'b': 2, 'c': 4})

        assert self['a'] == 1, self['a']
        assert self['b'] == 0, self['b']
        assert self['c'] == 0, self['c']
        expected = (0.25 * 1 ** 0.5 + 0.25 * 2 **
                    0.5 + 0.5 * 4 ** 0.5) ** (1 / 0.5)
        assert self['consumption_good'] == expected, (
            self['consumption_good'], expected)
        self.destroy('a', 1)
        self.destroy('consumption_good', expected)

        self.create('a', 2)
        self.create('b', 2)
        self.create('c', 2)
        self.create('d', 2)
        self.create('e', 2)
        self.produce(self.ces_flexible, {
                     'a': 1, 'b': 2, 'c': 2, 'd': 2, 'e': 2})

        assert self['a'] == 1, self['a']
        assert self['b'] == 0, self['b']
        assert self['c'] == 0, self['c']
        assert self['d'] == 0, self['d']
        assert self['e'] == 0, self['e']
        expected = (2 * (0.2 * 1 ** 0.5 + 0.2 * 2 ** 0.5 + 0.2 *
                    2 ** 0.5 + 0.2 * 2 ** 0.5 + 0.2 * 2 ** 0.5) **
                    (1 / 0.5))
        assert is_zero(self['consumption_good'] - expected), (
            self['consumption_good'], expected)
        self.destroy('a', 1)
        self.destroy('consumption_good', expected)

    def all_tests_completed(self):
        if self.time == self.last_round and self.id == 0:
            print('Test produce:                            \tOK')
            print('Test create_production_function_one_good:\tOK')
            print('Test create_cobb_douglas:                \tOK')
            print('Test leontief:                           \tOK')
            print('Test create_production_function_many_goods\tOK')
            print('Test predict_produce_output               \tOK')
            print('Test predict_produce_input                \tOK')
            print('Test net_value                            \tOK')
            print('Test predict_net_value                    \tOK')
