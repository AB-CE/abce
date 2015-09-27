""" The market agent
has the demand function q = 102 - p
"""
from __future__ import division
import abce


class Market(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        self.set_cobb_douglas_utility_function({'cookies': 1})

    def buying(self):
        """ buy a cookies if it is smaller then self.idn * 10. create enough
        money to by one cookies, if its cheap enough (its a partial equilibrium
        model)
        """
        offer = self.get_offers('cookies')[0]
        quantity = 102 - offer['price']
        self.message('firm', 0, 'demand', quantity)
        if quantity < 0:
            quantity = 0
        if quantity > offer['quantity']:
            quantity = offer['quantity']
        self.create('money', quantity * offer['price'] - self.possession('money'))
        self.accept_partial(offer, quantity)

    def consumption(self):
        """ consume the cookie """
        self.consume_everything()
