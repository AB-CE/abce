# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you
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
The :class:`abceagent.Agent` class is the basic class for creating your agent.
It automatically handles the
possession of goods of an agent. In order to produce/transforme goods you
need to also subclass the :class:`abceagent.Firm` [1]_ or to create a
consumer the :class:`abceagent.Household`.

For detailed documentation on:

Trading:
    see :class:`abceagent.Trade`

Logging and data creation:
    see :class:`abceagent.Database` and :doc:`simulation_results`

Messaging between agents:
    see :class:`abceagent.Messaging`.

.. autoexception:: abce.NotEnoughGoods

.. [1] or :class:`abceagent.FirmMultiTechnologies` for  complex technologies.
"""
from collections import OrderedDict


class Database:
    """ The database class """
    def __init__(self, id, agent_parameters, simulation_parameters, group, trade_logging,
                 database, check_unchecked_msgs, expiring, perishable, resource_endowment, start_round=None):
        super(Database, self).__init__(id, agent_parameters, simulation_parameters, group, trade_logging, database,
                                       check_unchecked_msgs, expiring, perishable, resource_endowment, start_round)

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
                data_to_write = {'%s_%s' % (str(action_name), str(
                    key)): data_to_log[key] for key in data_to_log}
            except TypeError:
                data_to_write = {str(action_name): data_to_log}

            self.database_connection.put(
                ["log",
                 self.group,
                 self.id,
                 self.round,
                 data_to_write,
                 action_name])

    def log_change(self, action_name, data_to_log):
        """ This command logs the change in the variable from the round before.
        Important, use only once with the same action_name.

        Args:
            'name'(string):
                the name of the current action/method the agent executes
            data_to_log:
                a dictianary with data for the database

        Examples::

            self.log_change('profit', {'money': self['money']]})
            self.log_change('inputs',
                {'money': self.possessions(['money', 'gold', 'CAP', 'LAB')]})
        """
        if self.log_this_round:
            data_to_write = {}
            try:
                for key in data_to_log:
                    data_to_write['%s_change_%s' % (
                        action_name, key)] = (
                            data_to_log[key] -
                            self._data_to_log_1[action_name][key])
            except KeyError:
                for key in data_to_log:
                    data_to_write['%s_change_%s' %
                                  (action_name, key)] = data_to_log[key]
            data_to_write['id'] = self.id
            self.database_connection.put(
                ["log", self.group, data_to_write, str(self.round)])

            self._data_to_log_1[action_name] = data_to_log

    def observe_begin(self, action_name, data_to_observe):
        """ observe_begin and observe_end, observe the change of a variable.
        observe_begin(...), takes a list of variables to be observed.
        observe_end(...) writes the change in this variables into the log file

        you can use nested observe_begin / observe_end combinations

        Args:
            'name'(string):
                the name of the current action/method the agent executes
            data_to_log:
                a dictianary with data for the database

        Example::

            self.log('production', {'composite': self.composite,
                self.sector: self.final_product[self.sector]})

            ... different method ...

            self.log('employment_and_rent', {
                'employment': self['LAB'],
                'rent': self['CAP']})
        """
        if self.log_this_round:
            self._data_to_observe[action_name] = data_to_observe

    def observe_end(self, action_name, data_to_observe):
        """ This command puts in a database called log, whatever values you
        want values need to be delivered as a dictionary:

        Args:
            'name'(string):
                the name of the current action/method the agent executes
            data_to_log:
                a dictianary with data for the database

        Example::

            self.log('production', {'composite': self.composite,
                self.sector: self.final_product[self.sector]})

            ... different method ...

            self.log('employment_and_rent', {
                'employment': self['LAB'],
                'rent':self['CAP']})
        """
        if self.log_this_round:
            before = self._data_to_observe.pop(action_name)
            data_to_write = {}
            for key in data_to_observe:
                data_to_write['%s_delta_%s' % (action_name, key)] = \
                    data_to_observe[key] - before[key]
            data_to_write['id'] = self.id
            self.database_connection.put(
                ["log", self.group, data_to_write, str(self.round)])

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
                                          str(self.round),
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
                                          self.id,
                                          str(self.round),
                                          data_to_write,
                                          serial])
