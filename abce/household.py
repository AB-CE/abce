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
The Household class extends the agent by giving him utility functions and the ability to consume goods.
"""
from __future__ import division
import compiler
import pyparsing as pp
import numpy as np
from tools import epsilon
save_err = np.seterr(invalid='ignore')


class Household:
    def utility_function(self):
        """ the utility function should be created with:
        set_cobb_douglas_utility_function,
        set_utility_function or
        set_utility_function_fast
        """
        return self._utility_function

    def consume_everything(self):
        """ consumes everything that is in the utility function
        returns utility according consumption

        A utility_function, has to be set before see
        py:meth:`~abceagent.Household.set_   utility_function`,
        py:meth:`~abceagent.Household.set_cobb_douglas_utility_function`

        Returns:
            A the utility a number. To log it see example.

        Example::

            utility = self.consume_everything()
            self.log('utility': {'u': utility})
        """
        return self.consume(dict((inp, self._haves[inp]) for inp in self._utility_function['input']))

    def consume(self, input_goods):
        """ consumes input_goods returns utility according to the agent's
        consumption function

        A utility_function, has to be set before see
        py:meth:`~abceagent.Household.set_   utility_function`,
        py:meth:`~abceagent.Household.set_cobb_douglas_utility_function` or

        Args:
            {'input_good1': amount1, 'input_good2': amount2 ...}:
                dictionary containing the amount of input good consumed.

        Raises:
            NotEnoughGoods: This is raised when the goods are insufficient.

        Returns:
            A the utility a number. To log it see example.

        Example::

            self.consumption_set = {'car': 1, 'ball': 2000, 'bike':  2}
            self.consumption_set = {'car': 0, 'ball': 2500, 'bike':  20}
            try:
                utility = self.consume(utility_function, self.consumption_set)
            except NotEnoughGoods:
                utility = self.consume(utility_function, self.smaller_consumption_set)
            self.log('utility': {'u': utility})

        """
        for good in self._utility_function['input']:
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(self.name, good, self._utility_function['input'][good] - self._haves[good])
        for good in self._utility_function['input']:
            self._haves[good] -= input_goods[good]
        goods_vector = input_goods.copy()
        goods_vector['utility'] = None
        exec(self._utility_function['code'], {}, goods_vector)
        return goods_vector['utility']

    def set_utility_function(self, formula, typ='from_formula'):
        """ creates a utility function from formula

        Utility_functions are then used as an argument in consume_with_utility,
        predict_utility and predict_utility_and_consumption.

        create_utility_function_fast is faster but more complicated utility_function

        Args:
            "formula": equation or set of equations that describe the
            utility function. (string) needs to start with 'utility = ...'

        Returns:
            A utility_function

        Example:
            formula = 'utility = ball + paint'
            self._utility_function = self.create_utility_function(formula)
            self.consume_with_utility(self._utility_function, {'ball' : 1, 'paint' : 2})

        //exponential is ** not ^
        """
        parse_single_input = pp.Suppress(pp.Word(pp.alphas + "_", pp.alphanums + "_")) + pp.Suppress('=') \
                + pp.OneOrMore(pp.Suppress(pp.Optional(pp.Word(pp.nums + '*/+-().[]{} ')))
                + pp.Word(pp.alphas + "_", pp.alphanums + "_"))
        parse_input = pp.delimitedList(parse_single_input, ';')

        self._utility_function = {}
        self._utility_function['type'] = typ
        self._utility_function['formula'] = formula
        self._utility_function['code'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input'] = list(parse_input.parseString(formula))

    def set_utility_function_fast(self, formula, input_goods, typ='from_formula'):
        """ creates a utility function from formula

        Utility_functions are then used as an argument in consume_with_utility,
        predict_utility and predict_utility_and_consumption.

        create_utility_function_fast is faster but more complicated

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are separated by a ;
            [output]: list of all output goods (left hand sides of the equations)

        Returns:
            A utility_function that can be used in produce etc.

        Example:
            formula = 'utility = ball + paint'

            self._utility_function = self.create_utility_function(formula, ['ball', 'paint'])
            self.consume_with_utility(self._utility_function, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        self._utility_function = {}
        self._utility_function['type'] = typ
        self._utility_function['formula'] = formula
        self._utility_function['code'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input'] = input_goods

    def set_cobb_douglas_utility_function(self, exponents):
        """ creates a Cobb-Douglas utility function

        Utility_functions are than used as an argument in consume_with_utility,
        predict_utility and predict_utility_and_consumption.

        Args:
            {'input1': exponent1, 'input2': exponent2 ...}: dictionary
            containing good names 'input' and correstponding exponents
        Returns:
            A utility_function that can be used in consume_with_utility etc.

        Example:
        self._utility_function = self.create_cobb_douglas({'bread' : 10, 'milk' : 1})
        self.produce(self.plastic_utility_function, {'bread' : 20, 'milk' : 1})
        """
        formula = 'utility=' + ('*'.join(['**'.join([input_good, str(input_quantity)]) for input_good, input_quantity in exponents.iteritems()]))
        self._utility_function = {}
        self._utility_function['type'] = 'cobb-douglas'
        self._utility_function['parameters'] = exponents
        self._utility_function['formula'] = formula
        self._utility_function['code'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input'] = exponents.keys()

    def predict_utility(self, input_goods):
        """ Predicts the utility of a vecor of input goods

            Predicts the utility of consume_with_utility(utility_function, input_goods)

        Args::

            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good used for the production.

        Returns::

            utility: Number

        Example::

            print(A.predict_utility(self._utility_function, {'ball': 2, 'paint': 1}))


        """
        goods_vector = input_goods.copy()
        goods_vector['utility'] = None
        exec(self._utility_function['code'], {}, goods_vector)
        return goods_vector['utility']


def sort(objects, key='price', reverse=False):
    """ Sorts the object by the key

    Args::

     reverse=True for descending

    Example::

        quotes_by_price = sort(quotes, 'price')
        """
    return sorted(objects, key=lambda objects: objects[key], reverse=reverse)
