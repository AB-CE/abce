
# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
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
# pylint: disable=W0201
""" The FirmMultiTechnologies class allows you to set up firm agents with
complex or several production functions. While the simple Firm automatically
handles one technology, FirmMultiTechnologies allows you to manage several
technologies manually.

The create_* functions allow you to create a technology and assign it to
a variable. :meth:`abce.FirmMultiTechnologies.produce` and similar
methods use this variable to produce with the according technology.
"""
from __future__ import division
import operator
from builtins import object
from functools import reduce
from abce.trade import get_epsilon
from abce.notenoughgoods import NotEnoughGoods
epsilon = get_epsilon()


class FirmMultiTechnologies(object):
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
        if production_function.use == 'all':
            for good in list(input_goods.keys()):
                if self._haves[good] < input_goods[good] - epsilon:
                    raise NotEnoughGoods(
                        self.name, good, (input_goods[good] - self._haves[good]))

            for good in input_goods:
                self._haves[good] -= input_goods[good]
        else:
            for good in list(production_function.use.keys()):
                if self._haves[good] < input_goods[good] - epsilon:
                    raise NotEnoughGoods(
                        self.name, good, (input_goods[good] - self._haves[good]))

            for good, use in production_function.use.items():
                self._haves[good] -= input_goods[good] * use

        output_dict = production_function.production(input_goods)
        for good in list(output_dict.keys()):
            self._haves[good] += output_dict[good]

        return output_dict

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

            def init(self):
                ...
                def production_function(goods)
                    return goods['a'] ** 0.25 * goods['b'] ** 0.5 * goods['c'] ** 0.25

                use = {'a': 1, 'b': 0.1, 'c': 0}

                self.production_function = self.create_production_function(production_function, use)

            def production(self):
                self.produce(self.production_function, {'a' : 1, 'b' : 2}
        """
        def dict_formula(goods):
            return {output: formula(goods)}
        production_function = ProductionFunction()
        production_function.production = dict_formula
        production_function.use = use
        return production_function

    def create_production_function_many_goods(self, formula, use):
        """ creates a production function that produces many goods

        A production function is a production process that produces
        several output goods from several input goods. It does so
        according to the formula given.
        Input goods are usually partially or completely used up.
        Production_functions can then ben used as an argument in
        :meth:`abce.FirmMultiTechnologies.produce`,
        :meth:`abce.FirmMultiTechnologies._predict_produce_output`
        :meth:`abce.FirmMultiTechnologies._predict_produce_input`

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

            def init(self):
                ...
                def production_function(goods)
                    output = {'soft_rubber': goods['a'] ** 0.25 * goods['b'] ** 0.5 * goods['c'] ** 0.25,
                              'hard_rubber': goods['a'] ** 0.1 * goods['b'] ** 0.2 * goods['c'] ** 0.01,
                              'waste': goods['b'] / 2}
                    return output

                use = {'a': 1, 'b': 0.1, 'c': 0}

                self.production_function = self.create_production_function(production_function, use)

            def production(self):
                self.produce(self.production_function, {'a' : 1, 'b' : 2, 'c': 5})
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

            def init(self):
                self.plastic_production_function = self.create_cobb_douglas('plastic', {'oil' : 10, 'labor' : 1}, 0.000001)

            ...

            def producing(self):
                self.produce(self.plastic_production_function, {'oil' : 20, 'labor' : 1})

        """
        def production_function(goods):
            return multiplier * reduce(operator.mul, [goods[name] ** exponent
                                                      for name, exponent in exponents.items()])

        def dict_formula(goods):
            return {output: production_function(goods)}
        production_function.production = dict_formula
        production_function.use = {name: 1 for name in list(exponents.keys())}
        return production_function

    def create_ces(self, output, gamma, multiplier=1, shares=None):
        """ creates a CES production function

        A production function is a production process that produces the
        given input  goods according to the CES formula to the output
        good:


        :math:`Q = F \\cdot \\left[\\sum_{i=1}^n a_{i}X_{i}^{\\gamma}\\ \\right]^{\\frac{1}{\\gamma}}`


        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Args:

            'output':
                Name of the output good

            gamma:
                elasticity of substitution :math:`= s =\\frac{1}{1-\\gamma}`

            multiplier:
                CES multiplier :math:`F`

            shares:
                :math:`a_{i}` = Share parameter of input i, :math:`\\sum_{i=1}^n a_{i} = 1`
                when share_parameters is not specified all inputs are weighted equally and
                the number of inputs is flexible.

        Returns:

            A production_function that can be used in produce etc.

        Example::

            self.stuff_production_function = self.create_ces('stuff', gamma=0.5, multiplier=1, shares={'labor': 0.25, 'stone':0.25, 'wood':0.5})
            self.produce(self.stuff_production_function, {'stone' : 20, 'labor' : 1, 'wood': 12})

        """
        if shares is None:
            def production_function(goods):
                a = 1 / len(goods)
                return multiplier * sum([a * goods[name] ** gamma
                                         for name in goods]) ** (1 / gamma)
            production_function.use = 'all'
        else:
            def production_function(goods):
                return multiplier * sum([share * goods[name] ** gamma
                                         for name, share in shares.items()]) ** (1 / gamma)
            production_function.use = {name: 1 for name in list(shares.keys())}

        def dict_formula(goods):
            return {output: production_function(goods)}
        production_function.production = dict_formula
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
            return min([goods[name] * factor for name, factor in utilization_quantities.items()])

        def dict_formula(goods):
            return {output: production_function(goods)}
        production_function.production = dict_formula
        production_function.use = {
            name: 1 for name in list(utilization_quantities.keys())}
        return production_function

    def _predict_produce_output(self, production_function, input_goods):
        return production_function.production(input_goods)

    def predict_produce_output(self, production_function, input_goods):
        """ Predicts the output of a certain input vector and for a given
            production function

            Predicts the production of produce(production_function, input_goods)

        Args::

            production_function:
                A production_function produced with
                create_production_function, create_cobb_douglas or create_leontief
            input_goods {'input_good1': amount1, 'input_good2': amount2 ...}:
                dictionary containing the amount of input good used for the production.

        Returns::

            A dictionary of the predicted output


        Example::

            print(A._predict_produce_output(car_production_function, two_cars))
            >>> {'car': 2}

        """
        return self._predict_produce_output(production_function, input_goods)

    def _predict_produce_input(self, production_function, input_goods):
        used_goods = {}
        for good, use in production_function.use.items():
            used_goods[good] = input_goods[good] * use
        return used_goods

    def predict_produce_input(self, production_function, input_goods):
        """ Returns a vector with input of goods

            Predicts the use of input goods, for a production.


        Args:
            production_function:
                A production_function produced with
                create_production_function, create_cobb_douglas or create_leontief
            input_goods: {'input_good1': amount1, 'input_good2': amount2 ...}:
                dictionary containing the amount of input good used for the production.

        Example::

            print(A._predict_produce_input(car_production_function, two_cars))

            >>> {'wheels': 4, 'chassi': 1}

        """
        return self._predict_produce_input(production_function, input_goods)

    def _net_value(self, produced_goods, used_goods, price_vector):
        revenue = sum([price_vector[good] * quantity for good,
                       quantity in list(produced_goods.items())])
        cost = sum([price_vector[good] * quantity for good,
                    quantity in list(used_goods.items())])
        return revenue - cost

    def net_value(self, produced_goods, used_goods, price_vector):
        """ Calculates the net_value of a goods_vector given a price_vector

            goods_vectors are vector, where the input goods are negative and
            the output goods are positive. When we multiply every good with its
            according price we can calculate the net_value of the corresponding
            production.
            goods_vectors are produced by predict_produce(.)


        Args:
            produced_goods:
                a dictionary with goods and quantities

            used_goods:
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
        return self._net_value(produced_goods, used_goods, price_vector)

    def _predict_net_value(self, production_function, input_goods, price_vector):
        output = self._predict_produce_output(production_function, input_goods)
        input = self._predict_produce_input(production_function, input_goods)
        return self.net_value(output, input, price_vector)

    def predict_net_value(self, production_function, input_goods, price_vector):
        """ Predicts the net value of a production, given a price vector


        Args:
            production_function:
                a production function

            input_goods:
                the goods to be used in the simulated production

            price_vector:
                vector of prices for input and output goods

        Example::

            input_goods = {'wheels': 4, 'chassi': 1}
            price_vector = {'wheels': 10, 'chassi': 100, 'car':1000}
            self.predict_net_value(self.consumption_good_production_function, input_goods, price_vector)

            >>> 860


        """
        return self._predict_net_value(production_function, input_goods, price_vector)

    def sufficient_goods(self, input_goods):
        """ checks whether the agent has all the goods in the vector input """
        for good in input_goods:
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(
                    self.name, good, input_goods[good] - self._haves[good])


class ProductionFunction(object):
    pass
