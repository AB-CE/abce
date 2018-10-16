from __future__ import division
from __future__ import print_function
import random
from abcEconomics.agent import Agent
from abcEconomics.notenoughgoods import NotEnoughGoods
from math import isclose


class Buy(Agent):
    def init(self, simulation_parameters, _,):
        self.last_round = simulation_parameters['num_rounds'] - 1
        self.tests = {'accepted': False, 'rejected': False, 'partial': False}
        self.price = 0
        if self.id == 1:
            self.tests['not_answered'] = False

    def one(self):
        """ Acts only if he is agent 0: sends an buy offer to agent 1 offer
        """
        if self.id == 0:
            self.create('money', random.uniform(0, 10000))
            self.money = self.possession('money')
            self.price = random.uniform(0.0001, 1)
            quantity = random.uniform(0, self.money / self.price)
            self.offer = self.buy('buy', 1, 'cookies', quantity, self.price)
            assert self.possession('money') == self.money - \
                quantity * self.price

    def two(self):
        """ Acts only if he is agent 1: receives offers and accepts;
        rejects; partially accepts and leaves offers unanswered.
        """
        if self.id == 1:
            self.create('cookies', random.uniform(0, 10000))
            cookies = self.possession('cookies')
            oo = self.get_offers('cookies')
            assert oo
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
                    assert self.possession(
                        'money') == offer.price * offer.quantity
                    assert self.possession(
                        'cookies') == cookies - offer.quantity
                    self.tests['accepted'] = True
                except NotEnoughGoods:
                    self.accept(offer, self.possession('cookies'))
                    assert isclose(self.possession('cookies'), 0)
                    assert self.possession('money') == cookies * offer.price
                    self.tests['partial'] = True

    def three(self):
        """
        """
        if self.id == 0:
            offer = self.offer
            if offer.status == 'rejected':
                test = self.money - self.possession('money')
                assert isclose(test, 0, abs_tol=0.0001), test
                self.tests['rejected'] = True
            elif offer.status == 'accepted':
                if offer.final_quantity == offer.quantity:
                    assert self.money - offer.quantity * \
                        offer.price == self.possession('money')

                    assert self.possession('cookies') == offer.quantity
                    self.tests['accepted'] = True
                else:
                    test = (self.money - offer.final_quantity *
                            offer.price) - self.possession('money')
                    assert isclose(test, 0.0, abs_tol=0.0001), test
                    test = self.possession('cookies') - offer.final_quantity
                    assert isclose(test, 0), test
                    self.tests['partial'] = True
            else:
                SystemExit('Error in buy')

    def laut(self):
        print("laut")
        self.haut = 'xxxx'

    def clean_up(self):
        self.destroy('money')
        self.destroy('cookies')

    def all_tests_completed(self):
        assert all(self.tests.values(
        )), 'not all tests have been run; abcEconomics workes correctly, restart the' \
            ' unittesting to do all tests %s' % self.tests
        if self.round == self.last_round and self.id == 0:
            print('Test abcEconomics.buy:\t\t\t\t\tOK')
            print('Test abcEconomics.accept\t(abcEconomics.buy):\t\tOK')
            print('Test abcEconomics.reject\t(abcEconomics.buy):\t\tOK')
            print('Test abcEconomics.accept, partial\t(abcEconomics.buy):\tOK')
            print('Test reject pending automatic \t(abcEconomics.buy):\tOK')
