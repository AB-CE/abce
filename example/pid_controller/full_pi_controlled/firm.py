#pylint: disable=C0103, W0142, W0613, R0904, R0902, R0901, W0201
""" This firm uses a PID controller to set the highest possible price at which
all it's goods can be sold.
"""
from __future__ import division
import abce
from abce.tools import is_zero, is_positive, is_negative, NotEnoughGoods #pylint: disable=W0611
import numpy as np
np.set_printoptions(suppress=True)
from picontroller import PiController
from upregression import UPRegression
from math import isnan, isinf


class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        self.price = self.price_1 = 100
        self.cookies_before = self.L = self.L_1 = 100
        self.wage = self.wage_1 = 1
        self.price_controller = PiController(0.01, 0.015, output0=self.price, positive=True)
        self.production_controller = PiController(0.01, 0.015, output0=self.L, positive=True)
        self.wage_controller = PiController(0.01, 0.015, output0=self.wage, positive=True)
        self.up_regression = UPRegression(memory=500)
        self.uw_regression = UPRegression(memory=500)
        self.set_leontief('cookies', {'labor': 1})

    def quote_hire(self):
        self.create('money', self.wage * self.L)
        self.quote_buy('labormarket', 0, 'labor', self.possession('money') / self.wage, self.wage)


    def hire(self):
        offer = self.get_offers('labor')[0]
        self.accept_partial(offer, min(offer['quantity'], self.possession('money') / self.wage, self.L))

        self.wage_1 = self.wage
        error = self.L - offer['quantity']
        self.wage = self.wage_controller.update(error)

        self.log('wage', {'wage': self.wage,
                          'error_cum': self.wage_controller.error_cum,
                          'error': error})


    def my_production(self):
        """ produce missing cookies """
        self.log('prodiction', self.produce_use_everything())
        self.log('cookies', {'inventory': self.possession('cookies')})

    def selling(self):
        self.offer = self.sell('market', 0, 'cookies', self.possession('cookies'), self.price)

    def adjust_price(self):
        self.total_orders = self.get_messages('demand')[0]['content']
        self.log('total', {'orders': self.total_orders})
        self.up_regression.fit(self.price, self.price_1, self.L, self.L_1)
        self.uw_regression.fit(self.wage, self.wage_1, self.L, self.L_1)

        self.price_1 = self.price
        error = -(self.possession('cookies') - self.cookies_before)
        self.cookies_before = self.possession('cookies')
        self.price = self.price_controller.update(error)

        self.log('price', {'price': self.price, 'error_cum': self.price_controller.error_cum, 'error': error, 'total_orders': self.total_orders})

    def adjust_quantity(self):
        if self.round % 20 == 19 and self.round > 50:
            w = self.wage
            p = self.price

            up = self.up_regression.predict()
            uw = self.uw_regression.predict()


            self.L_1 = self.L
            error =  p + up - (w + uw)
            #error =  p + up * self.L - (w + uw * self.L)
            self.L = self.production_controller.update(error)

            self.log('production', {'production': self.L,
                                    'error_cum': self.production_controller.error_cum,
                                    'error': error})

            self.log('up', {'chosen': up,
                            'complex_estimation': self.up_regression.up_delta_price,
                            'simple_estimation': self.up_regression.up_price})

            self.log('uw', {'chosen': uw,
                            'complex_estimation': self.uw_regression.up_delta_price,
                            'simple_estimation': self.uw_regression.up_price})
