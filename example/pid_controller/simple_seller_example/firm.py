""" This firm uses a PID controller to set the highest possible price at which
all it's goods can be sold.
"""
from __future__ import division
import abce
from abce.tools import NotEnoughGoods


class Firm(abce.Agent, abce.Firm, abce.Quote):
    def init(self, simulation_parameters, agent_parameters):
        self.error_cum = 0
        self.price = 20

    def production(self):
        """ produce missing cookies """
        self.create('cookies', 4 - self.possession('cookies'))

    def quote(self):
        """ make a non binding quote at self.price """
        for idn in range(10):
            self.quote_sell('household', idn, 'cookies', self.possession('cookies'), self.price)

    def selling(self):
        """ sell to all agents that accepted the price cookies, if there are
        not enough cookies, not all households are served. (ABCE makes sure
        that who is served is random)
        """
        orders = self.get_offers('cookies', descending=True)
        for order in orders:
            try:
                self.accept(order)
            except NotEnoughGoods:
                break

        total_orders = sum([order['quantity'] for order in orders])
        error = total_orders - 4
        self.error_cum += error
        self.price = max(0, 0.15 * error + 0.1 * self.error_cum)
        self.log('', {'price': self.price, 'error_cum': self.error_cum, 'error': error})
