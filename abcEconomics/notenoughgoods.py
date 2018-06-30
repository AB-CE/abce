
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
""" This file defines the :exc:`tools.NotEnoughGoods` """


class NotEnoughGoods(Exception):
    """ Methods raise this exception when the agent has less goods than needed

    These functions (self.produce, self.offer, self.sell, self.buy)
    should be encapsulated by a try except block::

     try:
        self.produce(...)
     except NotEnoughGoods:
        alternative_statements()

    """

    def __init__(self, _agent_name, good, amount_missing):
        self.good = good
        self.amount_missing = amount_missing
        self.name = _agent_name
        Exception.__init__(self)

    def __str__(self):
        return repr(str(self.name) + " " + str(self.amount_missing) + " of good '" + str(self.good) + "' missing")
