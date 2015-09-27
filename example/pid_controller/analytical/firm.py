#pylint: disable=C0103
""" This firm uses a PID controller to set the highest possible price at which
all it's goods can be sold.
"""
from __future__ import division
import abce
import numpy as np
from picontroller import PiController


np.set_printoptions(suppress=True)


class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        self.price_controller = PiController(0.001, 0.015, positive=True)
        self.production_controller = PiController(0.001, 0.015, positive=True)
        self.price = self.price_1 = 100
        self.total_orders = 0
        self.dX = np.ones((20, 4))
        self.dy = np.ones(20)
        self.X = np.ones((20, 2))
        self.y = np.ones(20)
        self.L = 4
        self.L_1 = 0
        self.production = 0

    def my_production(self):
        """ produce missing cookies """
        self.create('cookies', self.L)
        self.cookies_before = self.possession('cookies')
        self.log('cookies', {'created': self.L, 'inventory': self.possession('cookies')})
        self.y[self.round % 20] = (self.price)
        self.dy[self.round % 20] = (self.price - self.price_1)

    def selling(self):
        self.offer = self.sell('market', 0, 'cookies', self.possession('cookies'), self.price)

    def adjust_price(self):
        self.total_orders = self.get_messages('demand')[0]['content']
        self.log('total', {'orders': self.total_orders})
        self.dX[self.round % 20] = [1, self.L, self.price_1, self.L_1]
        self.X[self.round % 20] = [1, self.L]

        self.price_1 = self.price
        error = self.total_orders - self.cookies_before
        self.price = self.price_controller.update(error)

        self.log('price', {'price': self.price,
                           'error_cum': self.price_controller.error_cum,
                           'error': error,
                           'total_orders': self.total_orders})

    def adjust_quantity(self):
        #uw ought to be 1 * L for monopolist, 0 for competitive
        #up ought to be -1 * L for monopolist, 0 for competitive
        if self.round % 20 == 19:

            # monopolist
            uw = 1 * self.L
            up = -1 * self.L
            w = 14 + self.L
            p = self.price

            error = p + up - w - uw
            self.L = self.production_controller.update(error)

            self.log('production', {'production': self.production,
                                    'error_cum': self.production_controller.error_cum,
                                    'error': error})
