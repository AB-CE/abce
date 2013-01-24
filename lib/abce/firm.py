# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""
The :class:`abceagent.Agent` class is the basic class for creating your agent. It automatically handles the
possession of goods of an agent. In order to produce/transforme goods you need to also subclass
the :class:`abceagent.Firm` [1]_ or to create a consumer the :class:`abceagent.Household`.

For detailed documentation on:

Trading:
    see :class:`abceagent.Trade`
Logging and data creation:
    see :class:`abceagent.Database` and :doc:`simulation_results`
Messaging between agents:
    see :class:`abceagent.Messaging`.

.. autoexception:: abcetools.NotEnoughGoods

.. [1] or :class:`abceagent.FirmMultiTechnologies` for simulations with complex technologies.
"""
from __future__ import division
import numpy as np
from firmmultitechnologies import FirmMultiTechnologies
save_err = np.seterr(invalid='ignore')


class Firm(FirmMultiTechnologies):
    """ The firm class allows you to declare a production function for a firm.
    :meth:`~Firm.set_leontief`, :meth:`~abecagent.Firm.set_production_function`
    :meth:`~Firm.set_cobb_douglas`,
    :meth:`~Firm.set_production_function_fast`
    (FirmMultiTechnologies, allows you to declare several) With :meth:`~Firm.produce`
    and :meth:`~Firm.produce_use_everything` you can produce using the
    according production function. You have several auxiliarifunctions
    for example to predict the production. When you multiply
    :meth:`~Firm.predict_produce` with the price vector you get the
    profitability of the prodiction.
    """
    #TODO Example
    def produce_use_everything(self):
        """ Produces output goods from all input goods.

        Example::

            self.produce_use_everything()
        """
        return self.produce(self.possessions_all())

    def produce(self, input_goods):
        """ Produces output goods given the specified amount of inputs.

        Transforms the Agent's goods specified in input goods
        according to a given production_function to output goods.
        Automatically changes the agent's belonging. Raises an
        exception, when the agent does not have sufficient resources.

        Args:
            {'input_good1': amount1, 'input_good2': amount2 ...}:
                dictionary containing the amount of input good used for the production.

        Raises:
            NotEnoughGoods:
                This is raised when the goods are insufficient.

        Example::

            self.set_cobb_douglas_production_function('car' ..)
            car = {'tire': 4, 'metal': 2000, 'plastic':  40}
            try:
                self.produce(car)
            except NotEnoughGoods:
                print('today no cars')
        """
        return FirmMultiTechnologies.produce(self, self._production_function, input_goods)

    def sufficient_goods(self, input_goods):
        """ checks whether the agent has all the goods in the vector input """
        FirmMultiTechnologies.sufficient_goods(self)

    def set_production_function(self, formula, typ='from_formula'):
        """  sets the firm to use a Cobb-Douglas production function from a
        formula.

        A production function is a produceation process that produces the given
        input given input goods according to the formula to the output goods.
        Production_functions are than used to produce, predict_vector_produce and
        predict_output_produce.

        create_production_function_fast is faster but more complicated

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are seperated by a ;

        Example::

            formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
            self.set_production_function(formula)
            self.produce({'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        self._production_function = self.create_production_function(formula, typ)

    def set_production_function_fast(self, formula, output_goods, input_goods, typ='from_formula'):
        """  sets the firm to use a Cobb-Douglas production function from a
        formula, with given outputs

        A production function is a produceation process that produces the given
        input given input goods according to the formula to the output goods.
        Production_functions are than used to produce, predict_vector_produce and
        predict_output_produce.

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are seperated by a ;
            [output]: list of all output goods (left hand sides of the equations)

        Example::

            formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
            self.production_function_fast(formula, 'golf', ['waste'])
            self.produce(self, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        self._production_function = self.create_production_function_fast(formula, output_goods, input_goods, typ)

    def set_cobb_douglas(self, output, multiplier, exponents):
        """  sets the firm to use a Cobb-Douglas production function.

        A production function is a produceation process that produces the
        given input given input goods according to the formula to the output
        good.

        Args:
            'output': Name of the output good
            multiplier: Cobb-Douglas multiplier
            {'input1': exponent1, 'input2': exponent2 ...}: dictionary
            containing good names 'input' and correstponding exponents

        Example::

            self.set_cobb_douglas('plastic', 0.000001, {'oil' : 10, 'labor' : 1})
            self.produce({'oil' : 20, 'labor' : 1})

        """
        self._production_function = self.create_cobb_douglas(output, multiplier, exponents)

    def set_leontief(self, output, utilization_quantities, multiplier=1, isinteger='int'):
        """ sets the firm to use a Leontief production function.

        A production function is a production process that produces the
        given input given input goods according to the formula to the output
        good.

        Warning, when you produce with a Leontief production_function all goods you
        put in the produce(...) function are used up. Regardless whether it is an
        efficient or wastefull bundle

        Args:
            'output': Name of the output good
            {'input1': utilization_quantity1, 'input2': utilization_quantity2 ...}: dictionary
            containing good names 'input' and correstponding exponents
            multiplier: multipler
            isinteger='int' or isinteger='': When 'int' produce only integer
            amounts of the good. When '', produces floating amounts.

        Example::

            self.create_leontief('car', {'tire' : 4, 'metal' : 1000, 'plastic' : 20}, 1)
            two_cars = {'tire': 8, 'metal': 2000, 'plastic':  40}
            self.produce(two_cars)
        """
        self._production_function = self.create_leontief(output, utilization_quantities, isinteger)

    def predict_produce_output_simple(self, input_goods):
        """ Calculates the output of a production (but does not produce)

            Predicts the production of produce(production_function, input_goods)
            see also: Predict_produce(.) as it returns a vector

        Args:
            {'input_good1': amount1, 'input_good2': amount2 ...}:
                dictionary containing the amount of input good used for the production.

        Example::

            print(A.predict_output_produce(two_cars))
            >>> {'car': 2}

        """
        return self.predict_produce_output(self._production_function, input_goods)

    def predict_produce_simple(self, input_goods):
        """ Returns a vector with input (negative) and output (positive) goods

            Predicts the production of produce(production_function, input_goods) and
            the use of input goods.
            net_value(.) uses a price_vector (dictionary) to calculate the
            net value of this production.

        Args:
            {'input_good1': amount1, 'input_good2': amount2 ...}:
                dictionary containing the amount of input good used for the production.

        Example::

         prices = {'car': 50000, 'tire': 100, 'metal': 10, 'plastic':  0.5}
         value_one_car = net_value(predict_produce(one_car), prices)
         value_two_cars = net_value(predict_produce(two_cars), prices)
         if value_one_car > value_two_cars:
             A.produce(one_car)
         else:
             A.produce(two_cars)
        """
        return self.predict_produce(self._production_function, input_goods)
