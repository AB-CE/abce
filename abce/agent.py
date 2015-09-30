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
The :class:`abce.agent.Agent` class is the basic class for creating your agents. It automatically handles the
possession of goods of an agent. In order to produce/transforme goods you also need to subclass
the :class:`abceagent.Firm` [1]_ or to create a consumer the :class:`abce.agent.Household`.

For detailed documentation on:

Trading:
    see :class:`abce.agent.Trade`
Logging and data creation:
    see :class:`abce.agent.Database` and :doc:`simulation_results`
Messaging between agents:
    see :class:`abce.agent.Messaging`.

.. autoexception:: abce.tools.NotEnoughGoods

.. [1] or :class:`abce.agent.FirmMultiTechnologies` for simulations with complex technologies.
"""
from __future__ import division
from collections import OrderedDict, defaultdict
import numpy as np
from abce.tools import *
save_err = np.seterr(invalid='ignore')
from database import Database
from networklogger import NetworkLogger
from trade import Trade, Offer
from messaging import Messaging, Message
import time
from copy import copy
import random
from abce.expiringgood import ExpiringGood
from pprint import pprint

class Agent(Database, NetworkLogger, Trade, Messaging):
    """ Every agent has to inherit this class. It connects the agent to the simulation
    and to other agent. The :class:`abceagent.Trade`, :class:`abceagent.Database` and
    :class:`abceagent.Messaging` classes are included. You can enhance an agent, by also
    inheriting from :class:`abceagent.Firm`.:class:`abceagent.FirmMultiTechnologies`
    or :class:`abceagent.Household`.

    For example::

        class Household(abceagent.Agent, abceagent.Household):
            def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
            abceagent.Agent.__init__(self, *_pass_to_engine)
    """
    def __init__(self, simulation_parameters, agent_parameters, name, idn, group, trade_logging, database, logger):
        self.idn = idn
        """ self.idn returns the agents idn READ ONLY"""
        self.name = name
        """ name of the agent, combination of group name and id READ ONLY"""
        self.name = '%s_%i:' % (group, idn)
        """ self.name returns the agents name, which is the group name and the
        id seperated by '_' e.G. "household_12" READ ONLY!
        """
        self.name_without_colon = '%s_%i' % (group, idn)
        self.group = group
        """ self.group returns the agents group or type READ ONLY! """
        #TODO should be group_address(group), but it would not work
        # when fired manual + ':' and manual group_address need to be removed
        self._out = []
        self.simulation_parameters = simulation_parameters
        """ The simulation parameters and the number of agents in other groups

         Useful entries:

            'num_rounds':
                 the total number of rounds in the simulation.
            'num_goup_name':
                the number of agents for each group in the simulation. e.G.
                'num_myagents'
        """
        self.agent_parameters = agent_parameters

        self.database_connection = database
        self.logger_connection = logger

        if trade_logging == 'individual':
            self.trade_logging = 1
        elif trade_logging == 'group':
            self.trade_logging = 2
        elif trade_logging == 'off':
            self.trade_logging = 0
        else:
            SystemExit('trade_logging wrongly defined in agent.__init__' + trade_logging)

        self._haves = defaultdict(float)

        #TODO make defaultdict; delete all key errors regarding self._haves as defaultdict, does not have missing keys
        self._haves['money'] = 0
        self._msgs = {}

        self.given_offers = OrderedDict()
        self.given_offers[None] = Offer(self.group, self.idn, '', '', '', 0, 1, buysell='', idn=None)
        self.given_offers[None]['status'] = 'accepted'
        self.given_offers[None]['status_round'] = 0
        self._open_offers = defaultdict(dict)
        self._answered_offers = OrderedDict()
        self._offer_count = 0
        self._reject_offers_retrieved_end_subround = []
        self._contract_requests = defaultdict(list)
        self._contract_offers = defaultdict(list)
        self._contracts_pay = defaultdict(list)
        self._contracts_deliver = defaultdict(list)
        self._contracts_payed = []
        self._contracts_delivered = []

        self._expiring_goods = []

        self._trade_log = defaultdict(int)
        self._data_to_observe = {}
        self._data_to_log_1 = {}
        self._quotes = {}
        self.round = 0
        """ self.round returns the current round in the simulation READ ONLY!"""
        self._perishable = []
        self._resources = []
        self.variables_to_track_panel = []
        self.variables_to_track_aggregate = []

    def possession(self, good):
        """ returns how much of good an agent possesses.

        Returns:
            A number.

        possession does not return a dictionary for self.log(...), you can use self.possessions([...])
        (plural) with self.log.

        Example:

            if self.possession('money') < 1:
                self.financial_crisis = True

            if not(is_positive(self.possession('money')):
                self.bancrupcy = True

        """
        return float(self._haves[good])

    def possessions(self, list_of_goods):
        """ returns a dictionary of goods and the corresponding amount an agent owns

        Argument:
            A list with good names. Can be a list with a single element.

        Returns:
            A dictionary, that can be used with self.log(..)

        Examples::

            self.log('buget', self.possesions(['money']))

            self.log('goods', self.possesions(['gold', 'wood', 'grass']))

            have = self.possessions(['gold', 'wood', 'grass']))
            for good in have:
                if have[good] > 5:
                    rich = True
        """
        return {good: float(self._haves[good]) for good in list_of_goods}

    def possessions_all(self):
        """ returns all possessions """
        return copy(self._haves)

    def possessions_filter(self, goods=None, but=None, match=None, beginswith=None, endswith=None):
        """ returns a subset of the goods an agent owns, all arguments
        can be combined.

        Args:
            goods (list, optional):
                a list of goods to return
            but(list, optional):
                all goods but the list of goods here.
            match(string, optional TODO):
                goods that match pattern
            beginswith(string, optional):
                all goods that begin with string
            endswith(string, optional)
                all goods that end with string
            is(string, optional TODO)
                'resources':
                    return only goods that are endowments
                'perishable':
                    return only goods that are perishable
                'resources+perishable':
                    goods that are both
                'produced_by_resources':
                    goods which can be produced by resources

        Example::

            self.consume(self.possessions_filter(but=['money']))
            # This is redundant if money is not in the utility function

        """
        if not(goods):
            goods = self._haves.keys()
        if but != None:
            try:
                goods = set(goods) - set(but)
            except TypeError:
                raise SystemExit("goods and / or but must be a list e.G. ['element1', 'element2']")
        if beginswith != None:
            new_goods = []
            for good in goods:
                if good.startswith(beginswith):
                    new_goods.append(good)
            goods = new_goods
        if endswith != None:
            new_goods = []
            for good in goods:
                if good.endswith(endswith):
                    new_goods.append(good)
            goods = new_goods
        return dict((good, self._haves[good]) for good in goods)

    def _offer_counter(self):
        """ returns a unique number for an offer (containing the agent's name)
        """
        self._offer_count += 1
        return (self.name, self._offer_count)

    def _advance_round(self):
        #TODO replace OrderedDict with {}
        offer_iterator = self._answered_offers.iteritems()
        recent_answerd_offers = OrderedDict()
        try:
            while True:
                offer_id, offer = offer_iterator.next()
                if offer['round'] == self.round:  # message from prelast round
                    recent_answerd_offers[offer_id] = offer
                    break
            while True:
                offer_id, offer = next(offer_iterator)
                recent_answerd_offers[offer_id] = offer
        except StopIteration:
            self._answered_offers = recent_answerd_offers

        keep = {}
        for key in self.given_offers:
            if not('status' in self.given_offers[key]):
                keep[key] = self.given_offers[key]
            elif self.given_offers[key]['status_round'] == self.round:
                keep[key] = self.given_offers[key]
        self.given_offers = keep

        # contracts
        self._contract_requests = defaultdict(list)
        self._contract_offers = defaultdict(list)
        self._contracts_payed = []
        self._contracts_delivered = []

        for good in self._contracts_deliver:
            self._contracts_deliver[good] = [contract for contract in self._contracts_deliver[good] if contract['end_date'] > self.round]

        for good in self._contracts_pay:
            self._contracts_pay[good] = [contract for contract in self._contracts_pay[good] if contract['end_date'] > self.round]

        # expiring goods
        for good in self._expiring_goods:
            self._haves[good]._advance_round()

        if self.trade_logging > 0:
            self.database_connection.put(["trade_log", self._trade_log, self.round])

        self._trade_log = defaultdict(int)

        if sum([len(offers) for offers in self._open_offers.values()]):
                pprint(self._open_offers)
                raise SystemExit('There are messages an agent send that have not'
                                 'been retrieved in this round get_offer(.)')

        self.round += 1

    def create(self, good, quantity):
        """ creates quantity of the good out of nothing

        Use create with care, as long as you use it only for labor and
        natural resources your model is macro-economically complete.

        Args:
            'good': is the name of the good
            quantity: number
        """
        self._haves[good] += quantity

    def create_timestructured(self, good, quantity):
        """ creates quantity of the time structured good out of nothing.
        For example::

            self.creat_timestructured('capital', [10,20,30])

        Creates capital. 10 units are 2 years old 20 units are 1 year old
        and 30 units are new.

        It can alse be used with a quantity instead of an array. In this
        case the amount is equally split on the years.::

            self.creat_timestructured('capital', 60)

        In this case 20 units are 2 years old 20 units are 1 year old
        and 20 units are new.

        Args:
            'good':
                is the name of the good

            quantity:
                an arry or number
        """
        length = len(self._haves[good].time_structure)
        try:
            for i in range(length):
                self._haves[good].time_structure[i] += quantity[i]
        except TypeError:
            for i in range(length):
                self._haves[good].time_structure[i] += quantity / length


    def _declare_expiring(self, good, duration):
        """ creates a good that has a limited duration
        """
        self._haves[good] = ExpiringGood(duration)
        self._expiring_goods.append(good)

    def destroy(self, good, quantity):
        """ destroys quantity of the good,

        Args::

            'good': is the name of the good
            quantity: number

        Raises::

            NotEnoughGoods: when goods are insufficient
        """
        self._haves[good] -= quantity
        if self._haves[good] < 0:
            self._haves[good] = 0
            raise NotEnoughGoods(self.name, good, quantity - self._haves[good])

    def destroy_all(self, good):
        """ destroys all of the good, returns how much

        Args::

            'good': is the name of the good
        """
        quantity_destroyed = self._haves[good]
        self._haves[good] = 0
        return quantity_destroyed

    def execute(self, command, incomming_messages):
        self._out = []
        self._clearing__end_of_subround(incomming_messages)
        del incomming_messages[:]
        getattr(self, command)()
        self.__reject_polled_but_not_accepted_offers()
        return self._out

    def execute_parallel(self, command, incomming_messages):
        self._out = []
        try:
            self._clearing__end_of_subround(incomming_messages)
            getattr(self, command)()
            self.__reject_polled_but_not_accepted_offers()
        except KeyboardInterrupt:
            return None
        except:
            time.sleep(random.random())
            raise
        return self

    def execute_internal(self, command):
        getattr(self, command)()


    def _register_resource(self, resource, units, product):
        self._resources.append((resource, units, product))

    def _produce_resource(self):
        for resource, units, product in self._resources:
            if resource in self._haves:
                try:
                    self._haves[product] += float(units) * self._haves[resource]
                except KeyError:
                    self._haves[product] = float(units) * self._haves[resource]

    def _register_perish(self, good):
        self._perishable.append(good)

    def _perish(self):
        for good in self._perishable:
            if good in self._haves:
                self._haves[good] = 0

    def _register_panel(self, possessions, variables):
        self.possessions_to_track_panel = possessions
        self.variables_to_track_panel = variables

    def _register_aggregate(self, possessions, variables):
        self.possessions_to_track_aggregate = possessions
        self.variables_to_track_aggregate = variables

    def panel(self):
        data_to_track = {}
        for possession in self.possessions_to_track_panel:
            data_to_track[possession] = self._haves[possession]

        for variable in self.variables_to_track_panel:
            data_to_track[variable] = self.__dict__[variable]
        self.database_connection.put(["panel",
                                       data_to_track,
                                       str(self.idn),
                                       self.group,
                                       str(self.round)])

    def aggregate(self):
        data_to_track = {}
        for possession in self.possessions_to_track_aggregate:
            data_to_track[possession] = self._haves[possession]

        for variable in self.variables_to_track_aggregate:
            data_to_track[variable] = self.__dict__[variable]
        self.database_connection.put(["aggregate",
                                       data_to_track,
                                       self.group,
                                       self.round])

    def __reject_polled_but_not_accepted_offers(self):
        to_reject = []
        for offers in self._open_offers.values():
            for offer in offers.values():
                if offer['open_offer_status'] == 'polled':
                    to_reject.append(offer)
        for offer in to_reject:
            self.reject(offer)

    def _clearing__end_of_subround(self, incomming_messages):
        """ agent receives all messages and objects that have been send in this
        subround and deletes the offers that where retracted, but not executed.

        '_o': registers a new offer
        '_d': delete received that the issuing agent retract
        '_a': clears a made offer that was accepted by the other agent
        '_p': counterparty partially accepted a given offer
        '_r': deletes an offer that the other agent rejected
        '_g': recive a 'free' good from another party
        """
        for typ, msg in incomming_messages:
            if typ == '_o':
                msg['open_offer_status'] = 'received'
                self._open_offers[msg['good']][msg['idn']] = msg
            elif typ == '_d':
                del self._open_offers[msg['good']][msg['idn']]
            elif typ == '_a':
                offer = self._receive_accept(msg)
                if self.trade_logging == 2:
                    self._log_receive_accept_group(offer)
                elif self.trade_logging == 1:
                    self._log_receive_accept_agent(offer)
            elif typ == '_p':
                offer = self._receive_partial_accept(msg)
                if self.trade_logging == 2:
                    self._log_receive_partial_accept_group(offer)
                elif self.trade_logging == 1:
                    self._log_receive_partial_accept_agent(offer)
            elif typ == '_r':
                self._receive_reject(msg)
            elif typ == '_g':
                self._haves[msg[0]] += msg[1]
            elif typ == '_q':
                self._quotes[msg['idn']] = msg
            elif typ == '!o':
                if msg['makerequest'] == 'r':
                    self._contract_requests[msg['good']].append(msg)
                else:
                    self._contract_offers[msg['good']].append(msg)
            elif typ == '+d':
                self._contracts_deliver[msg['good']].append(msg)
            elif typ == '+p':
                self._contracts_pay[msg['good']].append(msg)
            elif typ == '!d':
                self._haves[msg['good']] += msg['quantity']
                self._contracts_delivered.append((msg['receiver_group'], msg['receiver_idn']))
                self._log_receive_accept(msg)
            elif typ == '!p':
                self._haves['money'] += msg['price']
                self._contracts_payed.append((msg['receiver_group'], msg['receiver_idn']))
                self._log_receive_accept(msg)
            else:
                self._msgs.setdefault(typ, []).append(Message(msg))


    def _send(self, receiver_group, receiver_idn, typ, msg):
        """ sends a message to 'receiver_group', who can be an agent, a group or
        'all'. The agents receives it at the begin of each round in
        self.messages(typ) is 'm' for mails.
        typ =(_o,c,u,r) are
        reserved for internally processed offers.
        """
        self._out.append([receiver_group, receiver_idn, (typ, msg)])

    def _send_to_group(self, receiver_group, typ, msg):
        """ sends a message to 'receiver_group', who can be an agent, a group or
        'all'. The agents receives it at the begin of each round in
        self.messages(typ) is 'm' for mails.
        typ =(_o,c,u,r) are
        reserved for internally processed offers.
        """
        raise NotImplementedError
        self._out.append([receiver_group, 'all', (typ, msg)])

def flatten(d, parent_key=''):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s_' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)

