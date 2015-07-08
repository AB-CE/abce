from __future__ import division
import abce
from abce.tools import *


class ProductionMultifirm(abce.Agent, abce.FirmMultiTechnologies):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abce.Agent.__init__(self, **_pass_to_engine)
        self.last_round = simulation_parameters['num_rounds'] - 1

        def mes(goods):
            return max(goods['a'] ** 2, goods['a'] ** 0.5 * goods['b'])
        use = {'a': 1, 'b': 0.1}

        self.pf = self.create_production_function_one_good(mes, 'consumption_good', use)
        self.cd = self.create_cobb_douglas('consumption_good', 5, {'a': 2, 'b': 1})
        self.leontief = self.create_leontief('consumption_good', {'a': 3, 'b': 1})

    def one(self):
        pass

    def two(self):
        pass

    def three(self):
        pass

    def clean_up(self):
        pass

    def production(self):
        self.create('a', 2)
        self.create('b', 2)
        self.produce(self.pf, {'a': 1, 'b': 2})

        assert self.possession('a') == 1, self.possession('a')
        assert self.possession('b') == 1.8, self.possession('b')
        assert self.possession('consumption_good') == 1 ** 0.5 * 2, self.possession('consumption_good')
        self.destroy('a', 1)
        self.destroy('b', 1.8)
        self.destroy('consumption_good', 1 ** 0.5 * 2)


        self.create('a', 2)
        self.create('b', 2)
        self.produce(self.cd, {'a': 1, 'b': 2})

        assert self.possession('a') == 1, self.possession('a')
        assert self.possession('b') == 0, self.possession('b')
        assert self.possession('consumption_good') == 5 * 1 ** 2 * 2 * 1, self.possession('consumption_good')
        self.destroy('a', 1)
        self.destroy('consumption_good', 5 * 1 ** 2 * 2 * 1)

        self.create('a', 2)
        self.create('b', 2)
        self.produce(self.leontief, {'a': 1, 'b': 2})

        assert self.possession('a') == 1, self.possession('a')
        assert self.possession('b') == 0, self.possession('b')
        assert self.possession('consumption_good') == min(1 * 3, 2 * 1), self.possession('consumption_good')
        self.destroy('a', 1)
        self.destroy('consumption_good', min(1 * 3, 2 * 1))


    def all_tests_completed(self):
        if self.round == self.last_round and self.idn == 0:
            print('Test produce:                            \tOK')
            print('Test create_production_function_one_good:\tOK')
            print('Test create_cobb_douglas:                \tOK')
            print('Test leontief:                           \tOK')

