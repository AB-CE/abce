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
from __future__ import absolute_import
from builtins import object
import operator
from functools import reduce
from ..trade import get_epsilon
epsilon = get_epsilon()


class Household(object):
    def get_utility_function(self):
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
        return self.consume({inp: self._haves[inp] for inp in list(self._utility_function.use.keys())})

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
            The utility as a number. To log it see example.

        Example::

            self.consumption_set = {'car': 1, 'ball': 2000, 'bike':  2}
            self.consumption_set = {'car': 0, 'ball': 2500, 'bike':  20}
            try:
                utility = self.consume(self.consumption_set)
            except NotEnoughGoods:
                utility = self.consume(self.smaller_consumption_set)
            self.log('utility': {'u': utility})

        """
        for good in list(self._utility_function.use.keys()):
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(
                    self.name, good, (input_goods[good] - self._haves[good]))

        for good, use in self._utility_function.use.items():
            self._haves[good] -= input_goods[good] * use

        return self._utility_function.formula(input_goods)

    def set_utility_function(self, formula, use):
        """ creates a utility function from a formula

        The formula is a function that takes a dictionary of goods
        as an argument and returns a floating point number, the utility.
        use is a dictionary containing the percentage use of the goods used in
        the consumption. Goods can be fully used (=1) for example food,
        partially used e.G. a car. And not used at all (=0) for example a
        house.

        Args:

            formula:
                a function that takes a dictionary of goods and
                computes the utility as a floating number.

            use:
                a dictionary that specifies for every good, how much
                it depreciates in percent.

        Example::

            self init(self):
                ...
                def utility_function(goods):
                    return goods['house'] ** 0.2 * good['food'] ** 0.6 + good['car'] ** 0.2

                {'house': 0, 'food': 1, 'car': 0.05}

                self.set_utility_function(utility_function, use)
        """
        self._utility_function = Utility_Function()
        self._utility_function.formula = formula
        self._utility_function.use = use

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
        def utility_function(goods):
            return reduce(operator.mul, [goods[name] ** exponent
                                         for name, exponent in exponents.items()])

        self._utility_function = Utility_Function()
        self._utility_function.formula = utility_function
        self._utility_function.use = {
            name: 1 for name in list(exponents.keys())}

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
        return self._utility_function.formula(input_goods)


class Utility_Function(object):
    pass
