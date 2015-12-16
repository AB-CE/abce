""" The market agent
has the demand function q = 102 - p
"""
from __future__ import division
import abce


class LaborMarket(abce.Agent, abce.Household, abce.Quote):
    def init(self, simulation_parameters, agent_parameters):
        self.set_cobb_douglas_utility_function({'cookies': 1})

    def accepting(self):
        """ buy a cookies if it is smaller then self.idn * 10. create enough
        money to by one cookies, if its cheap enough (its a partial equilibrium
        model)
        """
        quote = self.get_quotes('labor')[0]
        quantity = max(0, quote['price'] - 14)
        self.create('labor', quantity)
        self.accept_quote_partial(quote, quantity)

    def consumption(self):
        """ consume the cookie """
        self.consume_everything()

