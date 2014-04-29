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
""" The FirmMultiTechnologies class allows you to set up firm agents with
complex or several production functions. While the simple Firm automatically
handles one technology, FirmMultiTechnologies allows you to manage several
technologies manually.

The create_* functions allow you to create a technology and assign it to
a variable. :meth:`abce.FirmMultiTechnologies.produce` and similar
methods use this variable to produce with the according technology.
"""
from __future__ import division
import compiler
try:
    import pyparsing as pp
except ImportError:
    pass
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
        return self.produce(production_function, {inp: self.possession(inp) for inp in production_function['input']}

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
            NotEnoughGoods: This is raised when the goods are insufficient.

        Example::

            car = {'tire': 4, 'metal': 2000, 'plastic':  40}
            bike = {'tire': 2, 'metal': 400, 'plastic':  20}
            try:
                self.produce(car_production_function, car)
            except NotEnoughGoods:
                A.produce(bike_production_function, bike)
        """
        for good in production_function['input']:
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(self.name, good, (input_goods[good] - self._haves[good]))
        for good in production_function['input']:
            self._haves[good] -= input_goods[good]
        goods_vector = {good: 0 for good in production_function['output']}
        goods_vector.update(input_goods)
        exec(production_function['code'], {}, goods_vector)
        for good in production_function['output']:
            self._haves[good] += goods_vector[good]
        return dict([(good, goods_vector[good]) for good in production_function['output']])

    def create_production_function(self, formula, typ='from_formula'):
        """ creates a production function from formula

        A production function is a production process that produces the
        given input  goods according to the formula to the output
        goods.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        create_production_function_fast is faster but more complicated

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are separated by a ;

        Returns:
            A production_function that can be used in produce etc.

        Example:
            formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
            self.production_function = self.create_production_function(formula)
            self.produce(self.production_function, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        try:
            parse_single_output = pp.Word(pp.alphas + "_", pp.alphanums + "_") + pp.Suppress('=') + pp.Suppress(pp.Word(pp.alphanums + '*/+-().[]{} '))
            parse_output = pp.delimitedList(parse_single_output, ';')
            parse_single_input = pp.Suppress(pp.Word(pp.alphas + "_", pp.alphanums + "_")) + pp.Suppress('=') \
                    + pp.OneOrMore(pp.Suppress(pp.Optional(pp.Word(pp.nums + '*/+-().[]{} '))) + pp.Word(pp.alphas + "_", pp.alphanums + "_"))
            parse_input = pp.delimitedList(parse_single_input, ';')
        except NameError:
            print('pyparsing could not be loaded without pyparsing, create_production_function does not work use create_production_function instead')
            raise

        production_function = {}
        production_function['type'] = typ
        production_function['formula'] = formula
        production_function['code'] = compiler.compile(formula, '<string>', 'exec')
        production_function['output'] = list(parse_output.parseString(formula))
        production_function['input'] = list(parse_input.parseString(formula))
        return production_function

    def create_production_function_fast(self, formula, output_goods, input_goods, typ='from_formula'):
        """ creates a production function from formula, with given outputs

        A production function is a production process that produces the
        given input goods according to the formula to the output
        goods.
        Production_functions are then used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are separated by a ;
            [output]: list of all output goods (left hand sides of the equations)

        Returns:
            A production_function that can be used in produce etc.

        Example:
            formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
            self.production_function = self.create_production_function(formula, 'golf', ['waste', 'paint'])
            self.produce(self.production_function, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        production_function = {}
        production_function['type'] = typ
        production_function['formula'] = formula
        production_function['code'] = compiler.compile(formula, '<string>', 'exec')
        production_function['output'] = output_goods
        production_function['input'] = input_goods
        return production_function

    def create_cobb_douglas(self, output, multiplier, exponents):
        """ creates a Cobb-Douglas production function

        A production function is a production process that produces the
        given input  goods according to the formula to the output
        good.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Args:
            'output': Name of the output good
            multiplier: Cobb-Douglas multiplier
            {'input1': exponent1, 'input2': exponent2 ...}: dictionary
            containing good names 'input' and corresponding exponents
        Returns:
            A production_function that can be used in produce etc.

        Example:
        self.plastic_production_function = self.create_cobb_douglas('plastic', {'oil' : 10, 'labor' : 1}, 0.000001)
        self.produce(self.plastic_production_function, {'oil' : 20, 'labor' : 1})

        """
        ordered_input = [input_good for input_good in exponents]
        formula = output + '=' + str(multiplier) + '*' + '*'.join('(%s)**%f' % (input_good, exponent) for input_good, exponent in exponents.iteritems())
        optimization = '*'.join(['(%s)**%f' % ('%s', exponents[good]) for good in ordered_input])
        production_function = {}
        production_function['type'] = 'cobb-douglas'
        production_function['parameters'] = exponents
        production_function['formula'] = formula
        production_function['multiplier'] = multiplier
        production_function['code'] = compiler.compile(formula, '<string>', 'exec')
        production_function['output'] = [output]
        production_function['input'] = ordered_input
        production_function['optimization'] = optimization
        return production_function


    def create_leontief(self, output, utilization_quantities, isinteger=''):
        """ creates a Leontief production function


        A production function is a production process that produces the
        given input  goods according to the formula to the output
        good.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Warning, when you produce with a Leontief production_function all goods you
        put in the produce(...) function are used up. Regardless whether it is an
        efficient or wasteful bundle

        Args:
            'output':
                Name of the output good
            utilization_quantities:
                a dictionary containing good names and corresponding exponents
            isinteger='int' or isinteger='':
                When 'int' produce only integer amounts of the good.
                When '', produces floating amounts. (default)

        Returns:
            A production_function that can be used in produce etc.

        Example:
        self.car_technology = self.create_leontief('car', {'tire' : 4, 'metal' : 1000, 'plastic' : 20}, 1)
        two_cars = {'tire': 8, 'metal': 2000, 'plastic':  40}
        self.produce(self.car_technology, two_cars)
        """
        uqi = utilization_quantities.iteritems()
        ordered_input = [input_good for input_good in utilization_quantities]
        coefficients = ','.join('%s/%f' % (input_good, input_quantity) for input_good, input_quantity in uqi)
        formula = output + ' = ' + isinteger + '(min([' + coefficients + ']))'
        opt_coefficients = ','.join('%s/%f' % ('%s', utilization_quantities[good]) for good in ordered_input)
        optimization = isinteger + '(min([' + opt_coefficients + ']))'
        production_function = {}
        production_function['type'] = 'leontief'
        production_function['parameters'] = utilization_quantities
        production_function['formula'] = formula
        production_function['isinteger'] = isinteger
        production_function['code'] = compiler.compile(formula, '<string>', 'exec')
        production_function['output'] = [output]
        production_function['input'] = ordered_input
        production_function['optimization'] = optimization
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
        goods_vector = input_goods.copy()
        for good in production_function['output']:
            goods_vector[good] = None
        exec(production_function['code'], {}, goods_vector)
        output = {}
        for good in production_function['output']:
            output[good] = goods_vector[good]
        return output


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
        goods_vector = input_goods.copy()
        result = defaultdict(int)
        for good in production_function['output']:
            goods_vector[good] = None
        exec(production_function['code'], {}, goods_vector)
        for goods in production_function['output']:
            result[good] = goods_vector[good]
        for goods in production_function['input']:
            result[good] = -goods_vector[good]
        return result


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
