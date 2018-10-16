import abcEconomics
from tools import is_zero
import random
from abcEconomics import NotEnoughGoods


class Sell(abcEconomics.Agent):
    def init(self, rounds):
        self.last_round = rounds - 1
        self.tests = {'accepted': False, 'rejected': False,
                      'partial': False, 'full_partial': False}
        if self.id == 1:
            self.tests['not_answered'] = False

    def one(self):
        if self.id % 2 == 0:
            self.create('cookies', random.uniform(0, 10000))
            self.cookies = self['cookies']
            self.price = random.uniform(0.0001, 1)
            quantity = random.uniform(0, self.cookies)
            self.offer = self.sell(receiver=('sell', self.id + 1),
                                   good='cookies', quantity=quantity, price=self.price)
            assert self.not_reserved('cookies') == self.cookies - quantity

    def two(self):
        if self.id % 2 == 1:
            self.create('money', random.uniform(0, 10000))
            money = self['money']
            oo = self.get_offers('cookies')
            assert oo, oo
            for offer in oo:
                if random.randrange(0, 10) == 0:
                    self.tests['not_answered'] = True
                    continue
                elif random.randrange(0, 10) == 0:
                    self.reject(offer)
                    assert self['money'] == money
                    assert self['cookies'] == 0
                    self.tests['rejected'] = True
                    break  # tests the automatic clean-up of polled offers
                try:
                    if random.randrange(2) == 0:
                        self.accept(offer)
                        assert self['cookies'] == offer.quantity
                        assert self['money'] == money - offer.quantity * offer.price
                        self.tests['accepted'] = True
                    else:
                        self.accept(offer, offer.quantity)
                        assert self['cookies'] == offer.quantity
                        assert self['money'] == money - offer.quantity * offer.price
                        self.tests['full_partial'] = True

                except NotEnoughGoods:
                    self.accept(offer, self['money'] / offer.price)
                    assert self['money'] < 0.00000001, self['money']
                    test = (self['money'] - money) - \
                        self['cookies'] / offer.price
                    assert test < 0.00000001, test
                    self.tests['partial'] = True

    def three(self):
        if self.id % 2 == 0:
            offer = self.offer
            if offer.status == 'rejected':
                assert is_zero(self.cookies - self['cookies'])
                self.tests['rejected'] = True
            elif offer.status == 'accepted':
                if offer.final_quantity == offer.quantity:
                    assert self.cookies - \
                        offer.quantity == self['cookies']
                    assert self['money'] == offer.quantity * offer.price
                    self.tests['accepted'] = True
                else:
                    test = (self.cookies - offer.final_quantity) - \
                        self['cookies']
                    assert is_zero(test), test
                    test = self['money'] - \
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
        if self.time == self.last_round and self.id == 0:
            assert all(self.tests.values(
            )), 'not all tests have been run; abcEconomics workes correctly, restart the unittesting to do all tests %s' % self.tests
            print('Test abcEconomics.buy:\t\t\t\t\tOK')
            print('Test abcEconomics.accept\t(abcEconomics.buy):\t\tOK')
            print('Test abcEconomics.reject\t(abcEconomics.buy):\t\tOK')
            print('Test abcEconomics.accept\t(abcEconomics.buy):\tOK')
            print('Test reject pending automatic \t(abcEconomics.buy):\tOK')
