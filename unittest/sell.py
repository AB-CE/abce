import abce
from tools import *
import random
from abce import NotEnoughGoods


class Sell(abce.Agent):
    def init(self, simulation_parameters, agent_parameters):
        self.last_round = simulation_parameters['rounds'] - 1
        self.tests = {'accepted': False, 'rejected': False,
                      'partial': False, 'full_partial': False}
        if self.id == 1:
            self.tests['not_answered'] = False

    def one(self):
        if self.id % 2 == 0:
            self.create('cookies', random.uniform(0, 10000))
            self.cookies = self.possession('cookies')
            self.price = random.uniform(0.0001, 1)
            quantity = random.uniform(0, self.cookies)
            self.offer = self.sell(receiver=('sell', self.id + 1),
                                   good='cookies', quantity=quantity, price=self.price)
            assert self.possession('cookies') == self.cookies - quantity

    def two(self):
        if self.id % 2 == 1:
            self.create('money', random.uniform(0, 10000))
            money = self.possession('money')
            oo = self.get_offers('cookies')
            assert oo
            for offer in oo:
                if random.randrange(0, 10) == 0:
                    self.tests['not_answered'] = True
                    continue
                elif random.randrange(0, 10) == 0:
                    self.reject(offer)
                    assert self.possession('money') == money
                    assert self.possession('cookies') == 0
                    self.tests['rejected'] = True
                    break  # tests the automatic clean-up of polled offers
                try:
                    if random.randrange(2) == 0:
                        self.accept(offer)
                        assert self.possession('cookies') == offer.quantity
                        assert self.possession(
                            'money') == money - offer.quantity * offer.price
                        self.tests['accepted'] = True
                    else:
                        self.accept(offer, offer.quantity)
                        assert self.possession('cookies') == offer.quantity
                        assert self.possession(
                            'money') == money - offer.quantity * offer.price
                        self.tests['full_partial'] = True

                except NotEnoughGoods:
                    self.accept(offer, self.possession('money') / offer.price)
                    assert self.possession(
                        'money') < 0.00000001, self.possession('money')
                    test = (self.possession('money') - money) - \
                        self.possession('cookies') / offer.price
                    assert test < 0.00000001, test
                    self.tests['partial'] = True

    def three(self):
        if self.id % 2 == 0:
            offer = self.offer
            if offer.status == 'rejected':
                assert is_zero(self.cookies - self.possession('cookies'))
                self.tests['rejected'] = True
            elif offer.status == 'accepted':
                if offer.final_quantity == offer.quantity:
                    assert self.cookies - \
                        offer.quantity == self.possession('cookies')
                    assert self.possession(
                        'money') == offer.quantity * offer.price
                    self.tests['accepted'] = True
                else:
                    test = (self.cookies - offer.final_quantity) - \
                        self.possession('cookies')
                    assert is_zero(test), test
                    test = self.possession('money') - \
                        offer.final_quantity * offer.price
                    assert is_zero(test), test
                    self.tests['partial'] = True
                    self.tests['full_partial'] = True
            else:
                SystemExit('Error in sell')

    def clean_up(self):
        self.destroy('cookies')
        self.destroy('money')

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            assert all(self.tests.values(
            )), 'not all tests have been run; ABCE workes correctly, restart the unittesting to do all tests %s' % self.tests
            print('Test abce.buy:\t\t\t\t\tOK')
            print('Test abce.accept\t(abce.buy):\t\tOK')
            print('Test abce.reject\t(abce.buy):\t\tOK')
            print('Test abce.accept\t(abce.buy):\tOK')
            print('Test reject pending automatic \t(abce.buy):\tOK')
