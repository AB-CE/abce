
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
""" This file contains functions to compare floating point variables to 0. All
variables in this simulation as in every computer programm are floating
point variables. Floating point variables are not exact. Therefore var_a == var_b
has no meaning. Further a variable that is var_c = 9.999999999999966e-30 is for our
purpose equal to zero, but var_c == 0 would lead to False.
:meth:`is_zero`, :meth:`is_positive` and :meth:`is_negative` work
around this problem by defining float epsilon and determine whether the variable is
sufficiently close to zero or not.

This file also defines the :exc:`tools.NotEnoughGoods`
"""
from __future__ import division
epsilon = 1 / 1000000


def is_zero(x):
    """ checks whether a number is sufficiently close to zero. All variables
    in abcEconomics are floating point numbers. Due to the workings of floating point
    arithmetic. If x is 1.0*e^-100 so really close to 0, x == 0 will be false;
    is_zero will be true.
    """
    return -epsilon < x < epsilon


def is_positive(x):
    """ checks whether a number is positive and sufficiently different from
    zero. All variables in abcEconomics are floating point numbers. Due to the workings
    of floating point arithmetic. If x is 1.0*e^-100 so really close to 0,
    x > 0 will be true, eventhough it is very very small;
    is_zero will be true.
    """
    return - epsilon <= x


def is_negative(x):
    """ see is positive """
    return x <= epsilon
