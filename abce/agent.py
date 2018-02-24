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
The :py:class:`abce.Agent` class is the basic class for creating your agents.
It automatically handles the possession of goods of an agent. In order to
produce/transforme goods you also need to subclass the :py:class:`abce.Firm` or
to create a consumer the :py:class:`abce.Household`.

For detailed documentation on:

Trading, see :doc:`Trade`

Logging and data creation, see :doc:`Database`.

Messaging between agents, see :doc:`Messaging`.
"""
from collections import defaultdict
from pprint import pprint
import abce
from .database import Database
from .trade import Trade
from .messaging import Messaging
from .goods import Goods


class DummyContracts:
    def _advance_round(self, round):
        pass


class Agent(Database, Trade, Messaging, Goods):
    """ Every agent has to inherit this class. It connects the agent to the
    simulation and to other agent. The :class:`abce.Trade`,
    :class:`abce.Database` and :class:`abce.Messaging` classes are included.
    An agent can also inheriting from :class:`abce.Firm`,
    :class:`abce.FirmMultiTechnologies` or :class:`abce.Household` classes.

    Every method can return parameters to the simulation.

    For example::

        class Household(abce.Agent, abce.Household):
            def init(self, simulation_parameters, agent_parameters):
                self.num_firms = simulation_parameters['num_firms']
                self.type = agent_parameters['type']
                ...

            def selling(self):
                for i in range(self.num_firms):
                    self.sell('firm', i, 'good', quantity=1, price=1)

            ...
            def return_quantity_of_good(self):
                return['good']


        ...

        simulation = Simulation()
        households = Simulation.build_agents(household, 'household',
                                             parameters={...},
                                             agent_parameters=[{'type': 'a'},
                                                               {'type': 'b'}])
        for r in range(10):
            simulation.advance_round(r)
            households.selling()
            print(households.return_quantity_of_good())



    """
    def __init__(self, id, agent_parameters, simulation_parameters, group, trade_logging,
                 database, check_unchecked_msgs, expiring, perishable, resource_endowment, start_round=None):
        """ Do not overwrite __init__ instead use a method called init instead.
        init is called whenever the agent are build.
        """
        super(Agent, self).__init__(id, agent_parameters, simulation_parameters, group, trade_logging,
                                    database, check_unchecked_msgs, expiring, perishable, resource_endowment,
                                    start_round)
        self.id = id
        """ self.id returns the agents id READ ONLY"""
        self.name = (group, id)
        """ self.name returns the agents name, which is the group name and the
        id
        """
        self.name_without_colon = '%s_%i' % (group, id)
        self.group = group
        """ self.group returns the agents group or type READ ONLY! """
        # TODO should be group_address(group), but it would not work
        # when fired manual + ':' and manual group_address need to be removed
        self.database_connection = database

        self.trade_logging = {'individual': 1,
                              'group': 2, 'off': 0}[trade_logging]

        self._out = []
        # TODO make defaultdict; delete all key errors regarding self._inventory as
        # defaultdict, does not have missing keys
        self._msgs = {}

        self._data_to_observe = {}
        self._data_to_log_1 = {}
        self.round = start_round
        """ self.round is depreciated"""
        self.time = start_round
        """ self.time, contains the time set with simulation.advance_round(time)
            you can set time to anything you want an integer or
            (12, 30, 21, 09, 1979) or 'monday' """
        self._resources = []
        self.variables_to_track_panel = []
        self.variables_to_track_aggregate = []
        self.inbox = []

        try:
            self._add_contracts_list()
        except AttributeError:
            self.contracts = DummyContracts()

        if hasattr(abce, 'conditional_logging'):
            self.conditional_logging = True
            self.log_rounds = abce.conditional_logging
        else:
            self.conditional_logging = False

        self.log_this_round = True

        self._check_every_round_for_lost_messages = check_unchecked_msgs

        for good, duration in expiring:
            self._declare_expiring(good, duration)

        for good in perishable:
            self._register_perish(good)

        for resource, units, product in resource_endowment:
            self._register_resource(resource, units, product)

    def init(self):
        """ This method is called when the agents are build.
        It can be overwritten by the user, to initialize the agents.
        Parameters are the parameters given to
        :py:meth:`abce.Simulation.build_agents`.

        Example::

            class Student(abce.Agent):
                def init(self, rounds, age, lazy, school_size):
                    self.rounds = rounds
                    self.age = age
                    self.lazy = lazy
                    self.school_size = school_size

                def say(self):
                    print('I am', self.age ' years old and go to a school
                    that is ', self.school_size')


            def main():
                sim = Simulation()
                students = sim.build_agents(Student, 'student',
                                            agent_parameters=[{'age': 12, lazy: True},
                                                              {'age': 12, lazy: True},
                                                              {'age': 13, lazy: False},
                                                              {'age': 14, lazy: True}],
                                            rounds=50,
                                            school_size=990)

        """
        print("Warning: agent %s has no init function" % self.group)

    def _check_for_lost_messages(self):
        for offer in list(self.given_offers.values()):
            if offer.made < self.round:
                print("in agent %s this offers have not been retrieved:" %
                      self.name_without_colon)
                for offer in list(self.given_offers.values()):
                    if offer.made < self.round:
                        print(offer.__repr__())
                raise Exception('%s_%i: There are offers have been made before'
                                'last round and not been retrieved in this'
                                'round get_offer(.)' % (self.group, self.id))

        if sum([len(offers) for offers in list(self._open_offers_buy.values())]):
            pprint(dict(self._open_offers_buy))
            raise Exception('%s_%i: There are offers an agent send that have '
                            'not been retrieved in this round get_offer(.)' %
                            (self.group, self.id))

        if sum([len(offers) for offers in list(self._open_offers_sell.values())]):
            pprint(dict(self._open_offers_sell))
            raise Exception('%s_%i: There are offers an agent send that have '
                            'not been retrieved in this round get_offer(.)' %
                            (self.group, self.id))

        if sum([len(offers) for offers in list(self._msgs.values())]):
            pprint(dict(self._msgs))
            raise Exception('(%s, %i): There are messages an agent send that '
                            'have not been retrieved in this round '
                            'get_messages(.)' % (self.group, self.id))

    def _advance_round(self, time):
        super()._advance_round(time)
        self._inventory._advance_round()
        self.contracts._advance_round(self.round)

        if self._check_every_round_for_lost_messages:
            self._check_for_lost_messages()

        for ingredient, units, product in self._resources:
            self._inventory.create(product, self[ingredient] * units)

        self.round = time
        self.time = time

        if self.conditional_logging:
            if self.round in self.log_rounds:
                print("***", self.round)
                self.log_this_round = True
            else:
                self.log_this_round = False

    def _execute(self, command, args, kwargs):
        self._clearing__end_of_subround(self.inbox)
        self.inbox.clear()
        self._begin_subround()
        ret = getattr(self, command)(*args, **kwargs)
        self._end_subround()
        self._reject_polled_but_not_accepted_offers()
        return ret

    def _post_messages(self, agents):
        for group, id, envelope in self._out:
            agents[group][id].inbox.append(envelope)
        self._out.clear()

    def _post_messages_multiprocessing(self, num_processes):
        out = self._out
        self._out = defaultdict(list)
        return out

    def _begin_subround(self):
        """ Overwrite this to make ABCE plugins, that need to do
        something at the beginning of every subround """
        pass

    def _end_subround(self):
        """ Overwrite this to make ABCE plugins, that need to do
        something at the beginning of every subround """
        pass

    def _send(self, receiver_group, receiver_id, typ, msg):
        """ sends a message to 'receiver_group', 'receiver_id'
        The agents receives it at the begin of each subround.
        """
        self._out.append(
            (receiver_group, receiver_id, (typ, msg)))

    def _send_multiprocessing(self, receiver_group, receiver_id, typ, msg):
        """ Is used to overwrite _send in multiprocessing mode.
        Requires that self._out is overwritten with a defaultdict(list) """
        self._out[receiver_id % self._processes].append(
            (receiver_group, receiver_id, (typ, msg)))

    def __del__(self):
        self._check_for_lost_messages()
