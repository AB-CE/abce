# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
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
"""
The Household class extends the agent by giving him utility functions and the ability to consume goods.
"""

import operator
from functools import reduce
from ..notenoughgoods import NotEnoughGoods
from .trader import get_epsilon
epsilon = get_epsilon()


class Household:
    def consume(self, utility_function, input_goods):
        """ consumes input_goods returns utility according to the agent's
        utility function.

        A utility_function, has to be set before see
        py:meth:`~abcEconomics.Household.create_cobb_douglas_utility_function` or
        manually; see example.

        Args:

            utility_function:
                A function that takes goods as parameters and returns
                a utility or returns (utility, left_over_dict). Where left_over_dict is
                a dictionary of all goods that are not completely consumed

            input goods dictionary or list:
                dictionary containing the amount of input good used consumed or
                a list of all goods that get completely consumed.
        Raises:
            NotEnoughGoods: This is raised when the goods are insufficient.

        Returns:
            The utility as a number. To log it see example.

        Example::

            def utility_function(car, cookies, bike):
                utility = car ** 0.5 * cookies ** 0.2 * bike ** 0.3
                cookies = 0  # cookies are consumed, while the other goods are not consumed
                return utility, locals()


            def utility_function(cake, cookies, bonbons):  # all goods get completely consumed
                utility = cake ** 0.5 * cookies ** 0.2 * bonbons ** 0.3
                return utility

            self.consumption_set = {'car': 1, 'cookies': 2000, 'bike':  2}
            self.consume_everything = ['car', 'cookies', 'bike']
            try:
                utility = self.consume(utility_function, self.consumption_set)
            except NotEnoughGoods:
                utility = self.consume(utility_function, self.consume_everything)
            self.log('utility': {'u': utility})

        """
        if not isinstance(input_goods, dict):
            input_goods = {good: self[good] for good in input_goods}

        utility_and_result = utility_function(**input_goods)

        try:
            utility, result = utility_and_result
        except TypeError:
            result = {}
            utility = utility_and_result

        for good, quantity in input_goods.items():
            if self._inventory.haves[good] - quantity + result.get(good, 0) < -epsilon:
                raise NotEnoughGoods

        for good, quantity in input_goods.items():
            self._inventory.haves[good] -= quantity

        for good, quantity in result.items():
            self._inventory.haves[good] += quantity

        return utility

    def create_cobb_douglas_utility_function(self, exponents):
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
        def utility_function(**goods):
            utility = reduce(operator.mul,
                             [goods[name] ** exponent
                              for name, exponent in exponents.items()])
            return utility
        return utility_function
