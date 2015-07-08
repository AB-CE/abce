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
#pylint: disable=W0201
""" The FirmMultiTechnologies class allows you to set up firm agents with
complex or several production functions. While the simple Firm automatically
handles one technology, FirmMultiTechnologies allows you to manage several
technologies manually.

The create_* functions allow you to create a technology and assign it to
a variable. :meth:`abce.FirmMultiTechnologies.produce` and similar
methods use this variable to produce with the according technology.
"""
from __future__ import division
from collections import defaultdict
import numpy as np
from abce.tools import epsilon, NotEnoughGoods
save_err = np.seterr(invalid='ignore')


class FirmMultiTechnologies:
    def produce_use_everything(self, production_function):
        """ Produces output goods from all input goods, used in this
        production_function, the agent owns.

        Args::

            production_function: A production_function produced with
            py:meth:`~abceagent.FirmMultiTechnologies.create_production_function`, py:meth:`~abceagent.FirmMultiTechnologies.create_cobb_douglas` or
            py:meth:`~abceagent.FirmMultiTechnologies.create_leontief`

        Example::

            self.produce_use_everything(car_production_function)
        """
        return self.produce(production_function, {inp: self.possession(inp) for inp in production_function['input']})

    def produce(self, production_function, input_goods):
        """ Produces output goods given the specified amount of inputs.

        Transforms the Agent's goods specified in input goods
        according to a given production_function to output goods.
        Automatically changes the agent's belonging. Raises an
        exception, when the agent does not have sufficient resources.

        Args:
            production_function:
                A production_function produced with py:meth:`~abceagent.FirmMultiTechnologies..create_production_function`,
                py:meth:`~abceagent.FirmMultiTechnologies..create_cobb_douglas` or py:meth:`~abceagent.FirmMultiTechnologies..create_leontief`
            input goods {dictionary}:
                dictionary containing the amount of input good used for the production.

        Raises:
            NotEnoughGoods:
                This is raised when the goods are insufficient.

        Example::

            car = {'tire': 4, 'metal': 2000, 'plastic':  40}
            bike = {'tire': 2, 'metal': 400, 'plastic':  20}
            try:
                self.produce(car_production_function, car)
            except NotEnoughGoods:
                A.produce(bike_production_function, bike)
        """
        for good in production_function.use.keys():
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(self.name, good, (input_goods[good] - self._haves[good]))

        for good, use in production_function.use.iteritems():
            self._haves[good] -= input_goods[good] * use

        production = {}
        output_dict =  production_function.production(input_goods)
        for good in output_dict.keys():
            self._haves[good] += output_dict[good]


    def create_production_function_one_good(self, formula, output, use):
        """ creates a production function, that produces one good

        A production function is a production process that produces the
        given input  goods according to the formula to the output
        goods and uses up some or all of the input goods.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        create_production_function_fast is faster but more complicated

        Args:

            formula:
                this is a method, that takes the possession dictionary
                as an input and returns a float.

            output:
                the name of the good 'string'

            use:
                a dictionary of how much percent of each good is used up in the
                process


        Returns:

            A production_function that can be used in produce etc.

        Example::

            def __init__(self):
                ...
                def production_function(goods)
                    return goods['a'] ** 0.25 * goods['b'] ** 0.5 * goods['c'] ** 0.25

                use = {'a': 1, 'b': 0.1, 'c': 0}

                self.production_function = self.create_production_function(production_function, use)

            def production(self):
                self.produce(self.production_function, {'a' : 1, 'b' : 2}
        """
        dict_formula = lambda goods: {output: formula(goods)}
        production_function = ProductionFunction()
        production_function.production = dict_formula
        production_function.use = use
        return production_function

    def create_production_function_many_goods(self, formula):
        """ creates a production function that produces many goods

        A production function is a production process that produces the
        given input  goods according to the formula to the output
        goods and uses up some or all of the input goods.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        create_production_function_fast is faster but more complicated

        Args:

            formula:
                this is a method, that takes a goods dictionary
                as an input and returns a dictionary with the newly created
                goods.

            use:
                a dictionary of how much percent of each good is used up in the
                process


        Returns:

            A production_function that can be used in produce etc.

        Example::

            def __init__(self):
                ...
                def production_function(goods)
                    output = {'soft_rubber':goods['a'] ** 0.25 * goods['b'] ** 0.5 * goods['c'] ** 0.25,
                              'hard_rubber':goods['a'] ** 0.1 * goods['b'] ** 0.2 * goods['c'] ** 0.01,
                              'waste' goods['b'] / 2}
                    return output

                use = {'a': 1, 'b': 0.1, 'c': 0}

                self.production_function = self.create_production_function(production_function, use)

            def production(self):
                self.produce(self.production_function, {'a' : 1, 'b' : 2}

        //exponential is ** not ^
        """
        production_function = ProductionFunction()
        production_function.production = formula
        production_function.use = use
        return production_function

    def create_cobb_douglas(self, output, multiplier, exponents):
        """ creates a Cobb-Douglas production function

        A production function is a production process that produces the
        given input  goods according to the Cobb-Douglas formula to the output
        good.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Args:

            'output':
                Name of the output good

            multiplier:
                Cobb-Douglas multiplier

            {'input1': exponent1, 'input2': exponent2 ...}:
                dictionary containing good names 'input' and corresponding exponents

        Returns:

            A production_function that can be used in produce etc.

        Example:
        self.plastic_production_function = self.create_cobb_douglas('plastic', {'oil' : 10, 'labor' : 1}, 0.000001)
        self.produce(self.plastic_production_function, {'oil' : 20, 'labor' : 1})

        """
        def production_function(goods):
            return multiplier * np.prod([goods[name] ** exponent for name, exponent in exponents.iteritems()])

        dict_formula = lambda goods: {output: production_function(goods)}
        production_function.production = dict_formula
        production_function.use = {name: 1 for name in exponents.keys()}
        return production_function


    def create_leontief(self, output, utilization_quantities):
        """ creates a Leontief production function

        A production function is a production process that produces the
        given input  goods according to the Leontief formula to the output
        good.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Args:

            'output':
                Name of the output good

            multiplier:
                dictionary of multipliers it min(good1 * a, good2 * b, good3 * c...)

            {'input1': exponent1, 'input2': exponent2 ...}:
                dictionary containing good names 'input' and corresponding exponents

        Returns:

            A production_function that can be used in produce etc.

        Example:
        self.car_production_function = self.create_leontief('car', {'wheel' : 4, 'chassi' : 1})
        self.produce(self.car_production_function, {'wheel' : 20, 'chassi' : 5})

        """
        def production_function(goods):
            return min([goods[name] * factor for name, factor in utilization_quantities.iteritems()])

        dict_formula = lambda goods: {output: production_function(goods)}
        production_function.production = dict_formula
        production_function.use = {name: 1 for name in utilization_quantities.keys()}
        return production_function

    def predict_produce_output(self, production_function, input_goods):
        """ Predicts the output of a certain input vector and for a given
            production function

            Predicts the production of produce(production_function, input_goods)
            see also: Predict_produce(.) as it returns a calculatable vector

        Args::

            production_function: A production_function produced with
            create_production_function, create_cobb_douglas or create_leontief
            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good used for the production.

        Returns::

            A dictionary of the predicted output


        Example::

            print(A.predict_output_produce(car_production_function, two_cars))
            >>> {'car': 2}

        """
        pass


    def predict_produce(self, production_function, input_goods):
        """ Returns a vector with input (negative) and output (positive) goods

            Predicts the production of produce(production_function, input_goods) and
            the use of input goods.
            net_value(.) uses a price_vector (dictionary) to calculate the
            net value of this production.

        Args:
            production_function: A production_function produced with
            create_production_function, create_cobb_douglas or create_leontief
            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good used for the production.

        Example::

         prices = {'car': 50000, 'tire': 100, 'metal': 10, 'plastic':  0.5}
         value_one_car = net_value(predict_produce(car_production_function, one_car), prices)
         value_two_cars = net_value(predict_produce(car_production_function, two_cars), prices)
         if value_one_car > value_two_cars:
            A.produce(car_production_function, one_car)
         else:
            A.produce(car_production_function, two_cars)
        """
        pass

    def net_value(self, goods_vector, price_vector):
        """ Calculates the net_value of a goods_vector given a price_vector

            goods_vectors are vector, where the input goods are negative and
            the output goods are positive. When we multiply every good with its
            according price we can calculate the net_value of the corresponding
            production.
            goods_vectors are produced by predict_produce(.)


        Args:
            goods_vector: a dictionary with goods and quantities
            e.G. {'car': 1, 'metal': -1200, 'tire': -4, 'plastic': -21}
            price_vector: a dictionary with goods and prices (see example)

        Example::

         prices = {'car': 50000, 'tire': 100, 'metal': 10, 'plastic':  0.5}
         value_one_car = net_value(predict_produce(car_production_function, one_car), prices)
         value_two_cars = net_value(predict_produce(car_production_function, two_cars), prices)
         if value_one_car > value_two_cars:
            produce(car_production_function, one_car)
         else:
            produce(car_production_function, two_cars)
        """
        ret = 0
        for good, quantity in goods_vector.items():
            ret += price_vector[good] * quantity
        return ret

    def sufficient_goods(self, input_goods):
        """ checks whether the agent has all the goods in the vector input """
        for good in input_goods:
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(self.name, good, input_goods[good] - self._haves[good])

class ProductionFunction:
    pass
