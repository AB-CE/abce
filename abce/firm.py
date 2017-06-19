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
The Firm class gives an Agent the ability to set production functions and
produce.
"""
from __future__ import division
from __future__ import absolute_import
from builtins import object
from .firmmultitechnologies import FirmMultiTechnologies


class Firm(FirmMultiTechnologies):
    """ The firm class allows you to declare a production function for a firm.
    :meth:`abce.Firm.set_leontief`, :meth:`abce.Firm.set_production_function`
    :meth:`abce.Firm.set_cobb_douglas`,
    :meth:`abce.Firm.set_production_function_fast`
    (FirmMultiTechnologies, allows you to declare several) With :meth:`abce.Firm.produce`
    and :meth:`abce.Firm.produce_use_everything` you can produce using the
    according production function. You have several auxiliary functions
    for example to predict the production. When you multiply
    :meth:`abce.Firm.predict_produce` with the price vector you get the
    profitability of the production.

    If you want to create a firm with more than one production technology, you,
    should use the :class:`abce.FirmMultiTechnologies` class.
    """
    # TODO Example

    def produce_use_everything(self):
        """ Produces output goods from all input goods.

        Example::

            self.produce_use_everything()
        """
        return self.produce(self.possessions())

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
        FirmMultiTechnologies.sufficient_goods(self, input_goods)

    def set_production_function(self, formula, output, use):
        """  Creates the firm's production functions from a formula.

        A production function is a production process that produces a
        given output good from several input goods. Once you have set
        a production function you can use :meth:`abce.Firm.produce` to
        produce.

        If you want to produce more than one output good try
        :meth:`abce.Firm.set_production_function_many_goods`

        Args:

            formula:
                this is a method, that takes the possession dictionary
                as an input and returns a float.

            output:
                the name of the good 'string'

            use:
                a dictionary of how much percent of each good is used up in the
                process

        Example::

            def init(self):
                ...
                def production_function(goods):
                    return goods['a'] ** 0.25 * goods['b'] ** 0.5 * goods['c'] ** 0.25

                use = {'a': 1, 'b': 0.1, 'c': 0}

                self.set_production_function(production_function, output='cookies' use=use)

            def production(self):
                self.produce({'a' : 1, 'b' : 2}
        """
        self._production_function = self.create_production_function_one_good(
            formula, output, use)

    def set_production_function_many_goods(self, formula, use):
        """ creates a production function that produces many goods

        A production function is a production process that produces the
        several output  goods according to the formula to the output
        goods and uses up some or all of the input goods.
        Production_functions are than used by produce,
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

            def init(self):
                ...
                def production_function(goods)
                    output = {'soft_rubber': goods['a'] ** 0.25 * goods['b'] ** 0.5 * goods['c'] ** 0.25,
                              'hard_rubber': goods['a'] ** 0.1 * goods['b'] ** 0.2 * goods['c'] ** 0.01,
                              'waste': goods['b'] / 2}
                    return output

                use = {'a': 1, 'b': 0.1, 'c': 0}

                self.set_production_function_many_goods(production_function, use)

            def production(self):
                self.produce({'a' : 1, 'b' : 2, 'c': 5})
        """
        self._production_function = self.create_production_function_many_goods(
            formula, use)

    def set_cobb_douglas(self, output, multiplier, exponents):
        """  sets the firm to use a Cobb-Douglas production function.

        A production function is a production process that produces the
        given input goods according to the formula to the output
        good.

        Args:
            'output': Name of the output good
            multiplier: Cobb-Douglas multiplier
            {'input1': exponent1, 'input2': exponent2 ...}: dictionary
            containing good names 'input' and corresponding exponents

        Example::

            self.set_cobb_douglas('plastic', 0.000001, {'oil' : 10, 'labor' : 1})
            self.produce({'oil' : 20, 'labor' : 1})

        """
        self._production_function = self.create_cobb_douglas(
            output, multiplier, exponents)

    def set_ces(self, output, gamma, multiplier=1, shares=None):
        """ creates a CES production function

        A production function is a production process that produces the
        given input  goods according to the CES formula to the output
        good:


        :math:`Q = F \\cdot \\left[\\sum_{i=1}^n a_{i}X_{i}^{\\gamma}\\ \\right]^{\\frac{1}{\\gamma}}`


        Production_functions are than used by in produce,
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
                the number of inputs is flexible. Share parameters are an array with good
                names as keys and the shares as values.

        Example::

            def init(self):
                self.set_ces('stuff', gamma=0.5, multiplier=1, shares={'labor': 0.25, 'stone':0.25, 'wood':0.5})

            ...


            def producing(self):
                self.produce({'stone' : 20, 'labor' : 1, 'wood': 12})

        """
        self._production_function = self.create_ces(
            output, gamma, multiplier, shares)

    def set_leontief(self, output, utilization_quantities, multiplier=1):
        """ sets the firm to use a Leontief production function.

        A production function is a production process that produces the
        given input given according to the formula to the output
        good.

        Warning, when you produce with a Leontief production_function all goods you
        put in the produce(...) function are used up. Regardless whether it is an
        efficient or wasteful bundle

        Args:
            'output': Name of the output good
            {'input1': utilization_quantity1, 'input2': utilization_quantity2 ...}: dictionary
            containing good names 'input' and corresponding exponents
            multiplier: multiplier
            isinteger='int' or isinteger='': When 'int' produces only integer
            amounts of the good. When '', produces floating amounts.

        Example::

            self.create_leontief('car', {'tire' : 4, 'metal' : 1000, 'plastic' : 20}, 1)
            two_cars = {'tire': 8, 'metal': 2000, 'plastic':  40}
            self.produce(two_cars)
        """
        self._production_function = self.create_leontief(
            output, utilization_quantities)

    def predict_produce_output(self, input_goods):
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

            print(A.predict_produce_output(car_production_function, two_cars))
            >>> {'car': 2}

        """
        return self._predict_produce_output(self._production_function, input_goods)

    def predict_produce_input(self, input_goods):
        """ Returns a vector with input of goods

            Predicts the use of input goods, for a production.


        Args:
            production_function:
                A production_function produced with
                create_production_function, create_cobb_douglas or create_leontief
            input_goods: {'input_good1': amount1, 'input_good2': amount2 ...}:
                dictionary containing the amount of input good used for the production.

        Example::

            print(A.predict_produce_input(car_production_function, two_cars))

            >>> {'wheels': 4, 'chassi': 1}

        """
        return self._predict_produce_input(self._production_function, input_goods)

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

    def predict_net_value(self, input_goods, price_vector):
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
        return self._predict_net_value(self._production_function, input_goods, price_vector)


class ProductionFunction(object):
    pass
