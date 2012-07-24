from __future__ import division
import abceagent
from abcetools import *
import random


class Buy(abceagent.Agent):
    def __init__(self, simulation_parameters, own_parameters, _pass_to_engine):
        abceagent.Agent.__init__(self, *_pass_to_engine)
        self.last_round = simulation_parameters['num_rounds'] - 1
        self.cut_of = simulation_parameters['cut_of']
        self.tests = {'accepted': False, 'rejected': False, 'partial': False}
        if self.idn == 1:
            self.tests['not_answered'] = False

    def one(self):
        if self.idn == 0:
            self.create('money', random.uniform(0, 10000))
            self.money = self.possession('money')
            self.price = random.uniform(0.0001, 1)
            quantity = random.uniform(0, self.money / self.price)
            self.offer = self.buy('buy', 1, 'cookies', quantity, self.price)
            assert self.possession('money') == self.money - quantity * self.price

    def two(self):
        if self.idn == 1:
            self.create('cookies', random.uniform(0, 10000))
            cookies = self.possession('cookies')
            oo = self.get_offers('cookies')
            for offer in oo:
                if random.randint(0, 10) == 0:
                    self.tests['not_answered'] = True
                    continue
                elif random.randint(0, 10) == 0:
                    self.reject(offer)
                    assert self.possession('money') == 0
                    assert self.possession('cookies') == cookies
                    self.tests['rejected'] = True
                    break  # tests the automatic clean-up of polled offers
                try:
                    self.accept(offer)
                    assert self.possession('money') == offer['price'] * offer['quantity']
                    assert self.possession('cookies') == cookies - offer['quantity']
                    self.tests['accepted'] = True
                except NotEnoughGoods:
                    self.accept_partial(offer, self.possession('cookies'))
                    assert is_zero(self.possession('cookies'))
                    assert self.possession('money') == cookies * offer['price']
                    self.tests['partial'] = True

    def three(self):
        if self.idn == 0:
            offer = self.info(self.offer)
            if offer['status'] == 'rejected':
                test = self.money - self.possession('money')
                assert is_zero(test), test
                self.tests['rejected'] = True
            elif offer['status'] == 'accepted':
                assert self.money - offer['quantity'] * offer['price'] == self.possession('money')
                assert self.possession('cookies') == offer['quantity']
                self.tests['accepted'] = True
            elif offer['status'] == 'partial':
                test = (self.money - offer['final_quantity'] * offer['price']) - self.possession('money')
                assert is_zero(test), test
                test = self.possession('cookies') - offer['final_quantity']
                assert is_zero(test), test
                self.tests['partial'] = True

    def clean_up(self):
        self.destroy_all('money')
        self.destroy_all('cookies')

    def all_tests_completed(self):
            assert all(self.tests.values()), self.tests
            if self.round == self.last_round and self.idn == 0:
                print('Test abceagent.buy:\t\t\t\t\tOK')
                print('Test abceagent.accept\t(abceagent.buy):\t\tOK')
                print('Test abceagent.reject\t(abceagent.buy):\t\tOK')
                print('Test abceagent.accept_partial\t(abceagent.buy):\tOK')
                print('Test reject pending automatic \t(abceagent.buy):\tOK')

