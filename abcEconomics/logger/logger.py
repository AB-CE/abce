# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# abcEconomics is open-source software. If you are using abcEconomics for your research you
# are requested the quote the use of this software.
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
The :class:`abcEconomics.Agent` class is the basic class for creating your agent.
It automatically handles the
possession of goods of an agent. In order to produce/transforme goods you
need to also subclass the :class:`abcEconomics.Firm` [1]_ or to create a
consumer the :class:`abcEconomics.Household`.

For detailed documentation on:

Trading:
    see :class:`abcEconomics.Trade`

Logging and data creation:
    see :class:`abcEconomics.Database` and :doc:`simulation_results`

Messaging between agents:
    see :class:`abcEconomics.Messenger`.

.. autoexception:: abcEconomics.NotEnoughGoods

.. [1] or :class:`abcEconomics.FirmMultiTechnologies` for  complex technologies.
"""
from collections import OrderedDict
import re

import abcEconomics


class Logger:
    """ The Logger class """
    def __init__(self, id, agent_parameters, simulation_parameters):
        super(Logger, self).__init__(id, agent_parameters, simulation_parameters)
        # unpack simulation_parameters
        database = simulation_parameters['database']
        trade_logging = simulation_parameters['trade_logging']

        self.database_connection = database

        self._data_to_log_1 = {}
        self._data_to_observe = {}

        if hasattr(abcEconomics, 'conditional_logging'):
            self.conditional_logging = True
            self.log_rounds = abcEconomics.conditional_logging
        else:
            self.conditional_logging = False
        self.log_this_round = True

        self.trade_logging = {'individual': 1,
                              'group': 2,
                              'off': 0}[trade_logging]

    def log(self, action_name, data_to_log):
        """ With log you can write the models data. Log can save variable
        states and and the working of individual functions such as production,
        consumption, give, but not trade(as its handled automatically). Sending
        a dictionary instead of several using several log statements with a
        single variable is faster.

        Args:
            'name'(string):
                the name of the current action/method the agent executes

            data_to_log:
                a variable or a dictionary with data to log in the the database

        Example::

            self.log('profit', profit)

            self.log('employment_and_rent',
                     {'employment': self['LAB'],
                     'rent': self['CAP'],
                     'composite': self.composite})

            self.log(self.produce_use_everything())

        See also:
            :meth:`~abecagent.Database.log_nested`:
                handles nested dictianaries

            :meth:`~abecagent.Database.log_change`:
                loges the change from last round

            :meth:`~abecagent.Database.observe_begin`:

        """
        if self.log_this_round:
            try:
                data_to_write = {re.sub('[^0-9a-zA-Z_]', '', '%s_%s' % (str(action_name), str(
                    key))): data_to_log[key] for key in data_to_log}
            except TypeError:
                data_to_write = {str(action_name): data_to_log}

            self.database_connection.put(
                ["log",
                 self.group,
                 self._str_name,
                 self._str_round,
                 data_to_write,
                 action_name])

    def _common_log(self, variables, possessions, functions, lengths):
        ret = OrderedDict()
        for var in variables:
            ret[var] = self.__dict__[var]
        for pos in possessions:
            ret[pos] = self._inventory[pos]
        for name, func in functions.items():
            ret[name] = func(self)
        for length in lengths:
            ret['len_' + length] = len(self.__dict__[length])
        return ret

    def _agg_log(self, variables, possessions, functions, lengths):
        if self.log_this_round:
            data_to_write = self._common_log(variables,
                                             possessions,
                                             functions,
                                             lengths)
            self.database_connection.put(["snapshot_agg",
                                          self._str_round,
                                          self.group,
                                          data_to_write])

    def _panel_log(self, variables, possessions, functions, lengths, serial):
        if self.log_this_round:
            data_to_write = self._common_log(variables,
                                             possessions,
                                             functions,
                                             lengths)
            self.database_connection.put(["log",
                                          self.group,
                                          self._str_name,
                                          self._str_round,
                                          data_to_write,
                                          serial])

    def custom_log(self, method, *args, **kwargs):
        """ send custom logging commands to database plugin, see :ref:`Database Plugins` """
        self.database_connection.put([method, args, kwargs])
