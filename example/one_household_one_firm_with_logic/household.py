from __future__ import division  # makes division work correctly
from builtins import range
import abce


class Household(abce.Agent, abce.Household):
    def init(self, parameters, agent_parameters):
        """ 1. labor_endowment, which produces, because of w.declare_resource(...)
        in start.py one unit of labor per month
        2. Sets the utility function to utility = consumption of good "GOOD"
        """
        self.create('adult', 1)
        self.num_firms = parameters['num_firms']
        self.alpha = alpha = 1 / self.num_firms
        cd = {"GOOD%i" % i: alpha for i in range(self.num_firms)}
        #creates {GOOD1: 1/3, GOOD2: 1/3, GOOD3: 1/3}
        self.set_cobb_douglas_utility_function(cd)
        self.current_utiliy = 0

    def sell_labor(self):
        """ offers one unit of labor to firm 0, for the price of 1 "money" """
        for i in range(self.num_firms):
            self.sell('firm', i,
                      good="labor",
                      quantity=1 / self.num_firms,
                      price=1)

    def buy_goods(self):
        """ receives the offers and accepts them one by one """
        money = self.possession("money")
        quotes = self.get_messages('quote')
        for quote in quotes:
            price = quote.content[1]
            self.buy('firm', quote.sender_id,
                     good=quote.content[0],
                     quantity=self.alpha * money / price ,
                     price=price)

    def consumption(self):
        """ consumes_everything and logs the aggregate utility. current_utiliy
        """
        self.current_utiliy = self.consume_everything()
        self.log_value('HH', self.current_utiliy)

