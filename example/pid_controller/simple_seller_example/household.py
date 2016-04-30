""" a Household, different Household agents have a different willingness to
pay. The willingness to pay is self.id * 10. Which results in a downward
sloping demand curve
"""
from __future__ import division
import abce


class Household(abce.Agent, abce.Household, abce.Quote):
    def init(self, simulation_parameters, agent_parameters):
        self.set_cobb_douglas_utility_function({'cookies': 1})

    def buying(self):
        """ buy a cookies if it is smaller then self.idn * 10. create enough
        money to by one cookies, if its cheap enough (its a partial equlibirum
        model)
        """
        quotes = self.get_quotes('cookies')
        for quote in quotes:
            if quote.price <= self.id * 10 and self.possession('cookies') == 0:
                self.create('money', quote['price'])
                self.accept_quote_partial(quote, min(1, quote['quantity']))

    def consumption(self):
        """ consume the cookie """
        self.consume_everything()
