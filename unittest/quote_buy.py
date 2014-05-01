from __future__ import division
import abce
from tools import *
import random


class QuoteBuy(abce.Agent):
    def __init__(self, simulation_parameters, own_parameters, _pass_to_engine):
        abce.Agent.__init__(self, *_pass_to_engine)
        self.last_round = simulation_parameters['num_rounds'] - 1
        self.cut_of = simulation_parameters['cut_of']
        if self.idn == 1:
            self.tests = {'accepted': False, 'not_answered': False, 'partial': False}

    def one(self):
        """ Acts only if he is agent 0: sends an buy quote to agent 1 quote
        """
        if self.idn == 0:
            self.create('money', random.uniform(0, 10000))
            self.money = self.possession('money')
            self.price = random.uniform(0.0001, 1)
            quantity = random.uniform(0, self.money / self.price)
            self.quote_buy('quotebuy', 1, 'cookies', quantity, self.price)


    def two(self):
        """ Acts only if he is agent 1: recieves quotes and accepts;
        rejects; partially accepts and leaves quotes unanswerd.
        """
        if self.idn == 1:
            self.create('cookies', random.uniform(0, 10000))
            cookies = self.possession('cookies')
            if random.randint(0, 1) == 0:
                quotes = self.get_quotes('cookies')
            else:
                quotes = self.get_quotes_all()
                quotes = quotes['cookies']
            assert quotes
            for quote in quotes:
                if random.randint(0, 1) == 0:
                    self.tests['not_answered'] = True
                    continue
                if self.possession('cookies') >= quote['quantity']:
                    self.accept_quote(quote)
                    self.final_money = quote['price'] * quote['quantity']
                    assert self.possession('cookies') == cookies - quote['quantity']
                    self.tests['accepted'] = True
                else:
                    self.accept_quote_partial(quote, self.possession('cookies'))
                    assert is_zero(self.possession('cookies'))
                    self.final_money = cookies * quote['price']
                    self.tests['partial'] = True

    def three(self):
        """
        """
        if self.idn == 0:
            offers = self.get_offers('cookies')
            for offer in offers:
                self.accept(offer)




    def clean_up(self):
        self.destroy_all('money')
        self.destroy_all('cookies')
        if self.idn == 1:
            self.final_money = self.possession('money')

    def all_tests_completed(self):
        if self.round == self.last_round and self.idn == 1:
            assert all(self.tests.values()), 'not all tests have been run; ABCE workes correctly, restart the unittesting to do all tests %s' % self.tests
            print('Test abce.quote_buy:\t\t\t\t\tOK')

