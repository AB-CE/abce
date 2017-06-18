# pylint: disable=C0103, W0142, W0613, R0904, R0902, R0901, W0201, W0232, E1101
""" This firm uses a pi controller to set t
"""
from __future__ import division
import abce
import numpy as np
np.set_printoptions(suppress=True)
from picontroller import PiController
from upregression import UPRegression


class Firm(abce.Agent, abce.Firm, abce.Quote):
    def init(self, simulation_parameters, agent_parameters):
        self.price = self.price_1 = 100
        self.cookies_before = self.production_target = self.production_target_1 = 100
        self.wage = self.wage_1 = 1
        self.price_controller = PiController(
            0.01, 0.015, output0=self.price, positive=True)
        self.production_controller = PiController(
            0.01, 0.015, output0=self.production_target, positive=True)
        self.wage_controller = PiController(
            0.01, 0.015, output0=self.wage, positive=True)
        self.up_regression = UPRegression(memory=500)
        self.uw_regression = UPRegression(memory=500)
        self.set_leontief('cookies', {'labor': 1})

    def quote_hire(self):
        """ sends a note to the labor market, that  it is willing to pay wage """
        self.create('money', self.wage * self.production_target)
        self.quote_buy('labormarket', 0, 'labor',
                       self.possession('money') / self.wage, self.wage)

    def hire(self):
        """ hires enough people to meet production_target*. Lets the pi-
        controller adjust the wage according to the shortag / excess of labor.

        *but not more than is offered and he can afford """
        offer = self.get_offers('labor')[0]
        self.accept(offer, min(offer.quantity, self.possession(
            'money') / self.wage, self.production_target))

        self.wage_1 = self.wage
        error = self.production_target - offer.quantity
        self.wage = self.wage_controller.update(error)

        self.log('wage', {'wage': self.wage,
                          'error_cum': self.wage_controller.error_cum,
                          'error': error})

    def my_production(self):
        """ produce using all workers cookies """
        self.log('production', self.produce_use_everything())
        self.log('cookies', {'inventory': self.possession('cookies')})

    def selling(self):
        """ offers to sell all cookies """
        self.offer = self.sell('market', 0, 'cookies',
                               self.possession('cookies'), self.price)

    def adjust_price(self):
        """ The prices are adjusted according to the change in inventory.
        up and uw estimates are updated
        """
        self.total_orders = self.get_messages('demand')[0].content
        self.log('total', {'orders': self.total_orders})
        self.up_regression.fit(self.price, self.price_1,
                               self.production_target, self.production_target_1)
        self.uw_regression.fit(self.wage, self.wage_1,
                               self.production_target, self.production_target_1)

        self.price_1 = self.price
        error = -(self.possession('cookies') - self.cookies_before)
        self.cookies_before = self.possession('cookies')
        self.price = self.price_controller.update(error)

        self.log('price', {'price': self.price, 'error_cum': self.price_controller.error_cum,
                           'error': error, 'total_orders': self.total_orders})

    def adjust_quantity(self):
        if self.round % 20 == 19 and self.round > 50:
            w = self.wage
            p = self.price

            up = self.up_regression.predict()
            uw = self.uw_regression.predict()

            self.production_target_1 = self.production_target
            error = p + up - (w + uw)
            #error =  p + up * self.production_target - (w + uw * self.production_target)
            self.production_target = self.production_controller.update(error)

            self.log('production', {'production': self.production_target,
                                    'error_cum': self.production_controller.error_cum,
                                    'error': error})

            self.log('up', {'chosen': up,
                            'complex_estimation': self.up_regression.up_delta_price,
                            'simple_estimation': self.up_regression.up_price})

            self.log('uw', {'chosen': uw,
                            'complex_estimation': self.uw_regression.up_delta_price,
                            'simple_estimation': self.uw_regression.up_price})
