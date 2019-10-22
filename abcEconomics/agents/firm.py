
# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
# abcEconomics is open-source software. If you are using abcEconomics for your research you are
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
""" The Firm class allows you to set up firm agents with
complex or several production functions. While the simple Firm automatically
handles one technology, Firm allows you to manage several
technologies manually.

The create_* functions allow you to create a technology and assign it to
a variable. :meth:`abcEconomics.Firm.produce` and similar
methods use this variable to produce with the according technology.
"""
import operator
from functools import reduce
from collections import ChainMap
from ..notenoughgoods import NotEnoughGoods
from .trader import get_epsilon
epsilon = get_epsilon()


class Firm:
    """ With :code:`self.produce` a firm produces a good using production functions.
    For example the following farm has a cobb-douglas production function:

    class Farm(abcEconomics.Agent, abcEconomics.Firm):
        def init(self):
            self.production_function = create_cobb_douglas({'land': 0.7,
                                                            'capital': 0.1,
                                                            'labor': 0.2})

        def firming(self):
            self.produce(self.production_function, {{'land': self['land'],
                                                     'capital': self['capital'],
                                                     'labor': 2}})

    Production functions can be auto generated with:
        - py:meth:`~abcEconomics.Firm.create_cobb_douglas` or
        - py:meth:`~abcEconomics.Firm.create_ces` or
        - py:meth:`~abcEconomics.Firm.create_leontief`

    or specified by hand:

    A production function looks like this::

        def production_function(wheels, steel, stearing_wheels, machines):
            result = {'car': min(wheels / 4, steel / 10, stearing_wheels),
                      'wheels': 0,
                      'steel': 0,
                      'steering_wheels': 0,
                      'machine': machine * 0.9}
            return result

    Or more readably like this:

        def production_function(wheels, steel, stearing_wheels, machines):
            car = min(wheels / 4, steel / 10, stearing_wheels)
            wheels = 0
            steel = 0
            stearing_wheels = 0
            machine = machine * 0.9
            return locals()

    This production function, produces one car for every four wheels, 10 tonnes of steel
    and one stearing_wheel, it also requires one machine.  Wheels, steel and stearing_wheels
    are completely used. The plant is not used and the machine depreciates by 10%.production.

    A production function can also produce multiple goods. The last line :code:`return locals()`,
    can not be omitted. It returns all variables you define in this function as a dictionary.
    """

    def produce(self, production_function, input_goods, results=False):
        """ Produces output goods given the specified amount of inputs.

        Transforms the Agent's goods specified in input goods
        according to a given production_function to output goods.
        Automatically changes the agent's belonging. Raises an
        exception, when the agent does not have sufficient resources.

        Args:
            production_function:
                A production_function produced with
                py:meth:`~abcEconomics.Firm.create_production_function`,
                py:meth:`~abcEconomics.Firm.create_cobb_douglas` or
                py:meth:`~abcEconomics.Firm.create_leontief`

            input goods dictionary or list:
                dictionary containing the amount of input good used for the production or
                a list of all goods that get completely used.

            results:
                If True returns a dictionary with the used and produced goods.

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

            self.produce(car_production_function, ['tire', 'metal', 'plastic'])  # produces using all goods

        """
        if not isinstance(input_goods, dict):
            input_goods = {good: self[good] for good in input_goods}

        result = production_function(**input_goods)

        for good, quantity in input_goods.items():
            if self._inventory.haves[good] - quantity + result.get(good, 0) < -epsilon:
                raise NotEnoughGoods

        for good, quantity in input_goods.items():
            self._inventory.haves[good] -= quantity

        for good, quantity in result.items():
            self._inventory.haves[good] += quantity

        if results:
            return {good: result.get(good, 0) - input_goods.get(good, 0)
                    for good in ChainMap(input_goods, result).keys()}

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
                self.plastic_production_function = create_cobb_douglas('plastic', {'oil' : 10, 'labor' : 1}, 0.000001)

            ...

            def producing(self):
                self.produce(self.plastic_production_function, {'oil' : 20, 'labor' : 1})

        """
        def production_function(**goods):
            ret = multiplier * reduce(operator.mul,
                                      [goods[name] ** exponent
                                       for name, exponent in exponents.items()])
            return {output: ret}
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

            self.stuff_production_function = create_ces('stuff', gamma=0.5, multiplier=1,
                                                        shares={'labor': 0.25, 'stone':0.25, 'wood':0.5})
            self.produce(self.stuff_production_function, {'stone' : 20, 'labor' : 1, 'wood': 12})

        """
        if shares is None:
            def production_function(**goods):
                a = 1 / len(goods)
                ret = multiplier * sum([a * goods[name] ** gamma
                                        for name in goods]) ** (1 / gamma)
                return {output: ret}
        else:
            def production_function(**goods):
                ret = multiplier * sum([share * goods[name] ** gamma
                                        for name, share in shares.items()]) ** (1 / gamma)
                return {output: ret}

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
        self.car_production_function = create_leontief('car', {'wheel' : 4, 'chassi' : 1})
        self.produce(self.car_production_function, {'wheel' : 20, 'chassi' : 5})

        """
        def production_function(**goods):
            ret = min([goods[name] * factor for name, factor in utilization_quantities.items()])
            return {output: ret}

        return production_function
