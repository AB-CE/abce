from builtins import object
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
from pyparsing import (Word, Suppress, Optional, OneOrMore, ParseException,
                       alphas, alphanums, nums)


class HouseholdFromGams(object):
    """ an agent must inherit HouseholdFromGams and (optional) pass the column
    header in the world_parameters.csv file that contains the link to the gams
    file.

    Example::

     class Firm(AgentEngine,HouseholdFromGams)
        def __init__(self, world_parameters, own_parameters, _pass_to_engine):
            AgentEngine.__init__(self, *_pass_to_engine)
            HouseholdFromGams.__init__(self, 'calibration.csv')

    Example with batch job in world_parameters.csv (has a column calibration_file_name)::

     class Firm(AgentEngine,HouseholdFromGams)
        def __init__(self, world_parameters, own_parameters, _pass_to_engine):
            AgentEngine.__init__(self, *_pass_to_engine)
            HouseholdFromGams.__init__(self, world_parameters['calibration_file_name'])



    """

    def __init__(self, cal_file='calibration.cal'):
        self.cal_file = cal_file

    def set_cobb_douglas_utility_function_from_gams(self):
        self.set_cobb_douglas_utility_function(
            read_list('share parameter in utility func.'))


gams_identifier = Word(alphas, alphanums + '_')
S = Suppress
Ot = Optional

decimalNumber = Word(nums, nums + ",") + Optional("." + OneOrMore(Word(nums)))


def joinTokens(tokens):
    return "".join(tokens)


decimalNumber.setParseAction(joinTokens)


def stripCommas(tokens):
    return tokens[0].replace(",", "")


decimalNumber.addParseAction(stripCommas)


def convertToFloat(tokens):
    return float(tokens[0])


decimalNumber.addParseAction(convertToFloat)


def read_names(name):
    grammar = S(name) + S(':') + OneOrMore(gams_identifier + Ot(S(',')))
    ret = []
    with open("calibration.cal", 'r') as cal_file:
        for line in cal_file:
            try:
                names = grammar.parseString(line)
                ret.extend(names.asList())
            except ParseException:
                pass
    return ret


def read_list(name):
    grammar = S(name) + S(':') + gams_identifier + S('=') + decimalNumber
    ret = {}
    with open("calibration.cal", 'r') as cal_file:
        for line in cal_file:
            try:
                key, value = grammar.parseString(line)
                ret[key] = value
            except ParseException:
                pass
    return ret


def read_from_table(name, column=None, row=None):
    if not(column):
        column = gams_identifier  # any column is goods
    else:
        column = Suppress(column)
    if not(row):
        row = gams_identifier  # any row is goods
    else:
        row = Suppress(row)
    grammar = S(name) + S(':') + column + S(',') + row + S('=') + decimalNumber
    ret = {}
    with open("calibration.cal", 'r') as cal_file:
        for line in cal_file:
            try:
                key, value = grammar.parseString(line)
                ret[key] = value
            except ParseException:
                pass
    return ret
