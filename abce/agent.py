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
The :class:`abceagent.Agent` class is the basic class for creating your agent. It automatically handles the
possession of goods of an agent. In order to produce/transforme goods you need to also subclass
the :class:`abceagent.Firm` [1]_ or to create a consumer the :class:`abceagent.Household`.

For detailed documentation on:

Trading:
    see :class:`abceagent.Trade`
Logging and data creation:
    see :class:`abceagent.Database` and :doc:`simulation_results`
Messaging between agents:
    see :class:`abceagent.Messaging`.

.. autoexception:: abcetools.NotEnoughGoods

.. [1] or :class:`abceagent.FirmMultiTechnologies` for simulations with complex technologies.
"""
from __future__ import division
import zmq
import multiprocessing
import compiler
import pyparsing as pp
from collections import OrderedDict, defaultdict
import numpy as np
from abce.tools import *
from inspect import getmembers, ismethod
from random import shuffle
save_err = np.seterr(invalid='ignore')
from database import Database
from logger import Logger
from trade import Trade, Offer
from messaging import Messaging, Message


class Agent(Database, Logger, Trade, Messaging, multiprocessing.Process):
    """ Every agent has to inherit this class. It connects the agent to the simulation
    and to other agent. The :class:`abceagent.Trade`, :class:`abceagent.Database` and
    :class:`abceagent.Messaging` classes are include. You can enhance an agent, by also
    inheriting from :class:`abceagent.Firm`.:class:`abceagent.FirmMultiTechnologies`
    or :class:`abceagent.Household`.

    For example::

        class Household(abceagent.Agent, abceagent.Household):
            def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
            abceagent.Agent.__init__(self, *_pass_to_engine)
    """
    def __init__(self, idn, group, _addresses, trade_logging):
        multiprocessing.Process.__init__(self)
        self.idn = idn
        self.name = '%s_%i:' % (group, idn)
        self.name_without_colon = '%s_%i' % (group, idn)
        self.group = group
        #TODO should be group_address(group), but it would not work
        # when fired manual + ':' and manual group_address need to be removed
        self._addresses = _addresses
        self._methods = {}
        self._register_actions()
        if trade_logging == 'individual':
            self._log_receive_accept = self._log_receive_accept_agent
            self._log_receive_partial_accept = self._log_receive_partial_accept_agent
        elif trade_logging == 'group':
            self._log_receive_accept = self._log_receive_accept_group
            self._log_receive_partial_accept = self._log_receive_partial_accept_group
        elif trade_logging == 'off':
            self._log_receive_accept = lambda: None
            self._log_receive_partial_accept = lambda: None
        else:
            SystemExit('trade_logging wrongly defined in agent.__init__' + trade_logging)

        self._haves = defaultdict(int)

        #TODO make defaultdict; delete all key errors regarding self._haves as defaultdict, does not have missing keys
        self._haves['money'] = 0
        self._msgs = defaultdict(list)

        self.given_offers = OrderedDict()
        self.given_offers[None] = Offer(self.group, self.idn, '', '', '', 0, 1, buysell='', idn=None)
        self.given_offers[None]['status'] = 'accepted'
        self.given_offers[None]['status_round'] = 0
        self._open_offers = {}
        self._answered_offers = OrderedDict()
        self._offer_count = 0
        self._reject_offers_retrieved_end_subround = []
        self._trade_log = defaultdict(int)
        self._data_to_observe = {}
        self._data_to_log_1 = {}
        self._quotes = {}

        self.round = 0

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
        return self._haves[good]

    def possessions(self, list_of_goods):
        """ returns a dictionary of goods and the correstponding amount an agent owns

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
        return {good: self._haves[good] for good in list_of_goods}

    def possessions_all(self):
        """ returns all possessions """
        return self._haves.copy()

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
                raise SystemExit("goods and/or but must be a list e.G. ['element1', 'element2']")
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
        return '%s:%i' % (self.name, self._offer_count)

    def _register_actions(self):
        """ registers all actions of the Agent, which do not start with '_' """
        for method in getmembers(self):
            if (ismethod(method[1]) and
                    not(method[0] in vars(Agent) or method[0].startswith('_') or method[0] in vars(multiprocessing.Process))):
                self._methods[method[0]] = method[1]
            self._methods['_advance_round'] = self._advance_round
            self._methods['_clearing__end_of_subround'] = self._clearing__end_of_subround
            self._methods['_db_panel'] = self._db_panel
            self._methods['_perish'] = self._perish
            self._methods['_produce_resource_rent_and_labor'] = self._produce_resource_rent_and_labor
            self._methods['_aesof'] = self._aesof
            #TODO inherited classes provide methods that should not be callable
            #change _ policy _ callable from outside __ not and exception lists

    def _advance_round(self):
        offer_iterator = self._answered_offers.iteritems()
        recent_answerd_offers = OrderedDict()
        try:
            while True:
                offer_id, offer = next(offer_iterator)
                if offer['round'] == self.round:  # message from prelast round
                    recent_answerd_offers[offer_id] = offer
                    break
            while True:
                offer_id, offer = next(offer_iterator)
                recent_answerd_offers[offer_id] = offer
        except StopIteration:
            self._answered_offers = recent_answerd_offers

        keep = OrderedDict()
        for key in self.given_offers:
            if not('status' in self.given_offers[key]):
                keep[key] = self.given_offers[key]
            elif self.given_offers[key]['status_round'] == self.round:
                keep[key] = self.given_offers[key]
        self.given_offers = keep

        self.database_connection.send("trade_log", zmq.SNDMORE)
        self.database_connection.send_pyobj(self._trade_log, zmq.SNDMORE)
        self.database_connection.send(str(self.round))

        self._trade_log = defaultdict(int)

        self.round += 1

    def create(self, good, quantity):
        """ creates quantity of the good out of nothing

        Use this create with care, as long as you use it only for labor and
        natural resources your model is macroeconomally complete.

        Args:
            'good': is the name of the good
            quantity: number
        """
        self._haves[good] += quantity

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

    def run(self):
        self.context = zmq.Context()
        self.commands = self.context.socket(zmq.SUB)
        self.commands.connect(self._addresses['command_addresse'])
        self.commands.setsockopt(zmq.SUBSCRIBE, "all")
        self.commands.setsockopt(zmq.SUBSCRIBE, self.name)
        self.commands.setsockopt(zmq.SUBSCRIBE, group_address(self.group))

        self.out = self.context.socket(zmq.PUSH)
        self.out.connect(self._addresses['frontend'])

        self.database_connection = self.context.socket(zmq.PUSH)
        self.database_connection.connect(self._addresses['database'])

        self.logger_connection = self.context.socket(zmq.PUSH)
        self.logger_connection.connect(self._addresses['logger'])

        self.messages_in = self.context.socket(zmq.DEALER)
        self.messages_in.setsockopt(zmq.IDENTITY, self.name)
        self.messages_in.connect(self._addresses['backend'])

        self.shout = self.context.socket(zmq.SUB)
        self.shout.connect(self._addresses['group_backend'])
        self.shout.setsockopt(zmq.SUBSCRIBE, "all")
        self.shout.setsockopt(zmq.SUBSCRIBE, self.name)
        self.shout.setsockopt(zmq.SUBSCRIBE, group_address(self.group))

        self.out.send_multipart(['!', '!', 'register_agent', self.name])

        while True:
            try:
                self.commands.recv()  # catches the group adress.
            except KeyboardInterrupt:
                print('KeyboardInterrupt: %s, Last command: %s in self.commands.recv() to catch own adress ~1888' % (self.name, command))
                break
            command = self.commands.recv()
            if command == "!":
                subcommand = self.commands.recv()
                if subcommand == 'die':
                    self.__signal_finished()
                    break
            try:
                self._methods[command]()
            except KeyError:
                if command not in self._methods:
                    raise SystemExit('The method - ' + command + ' - called in the agent_list is not declared (' + self.name)
                else:
                    raise
            except KeyboardInterrupt:
                print('KeyboardInterrupt: %s, Current command: %s ~1984' % (self.name, command))
                break

            if command[0] != '_':
                self.__reject_polled_but_not_accepted_offers()
                self.__signal_finished()
        #self.context.destroy()

    def _produce_resource_rent_and_labor(self):
        resource, units, product = self.commands.recv_multipart()
        if resource in self._haves:
            try:
                self._haves[product] += float(units) * self._haves[resource]
            except KeyError:
                self._haves[product] = float(units) * self._haves[resource]

    def _perish(self):
        goods = self.commands.recv_multipart()
        for good in goods:
            if good in self._haves:
                self._haves[good] = 0
            for key in self._open_offers.keys():
                if self._open_offers[key]['good'] == good:
                    del self._open_offers[key]

            for key in self.given_offers.keys():
                if (self.given_offers[key]['good'] == good
                   and not(self.given_offers[key]['status'] == 'perished')):
                    self.given_offers[key]['status'] = 'perished'
                    self.given_offers[key]['status_round'] = self.round

    def _db_panel(self):
        command = self.commands.recv()
        try:
            data_to_track = self._methods[command]()
        except KeyError:
            data_to_track = self._haves
        #TODO this leads to ambigues errors when there is a KeyError in the data_to_track
        #method (which is common), but testing takes to much time
        self.database_connection.send("panel", zmq.SNDMORE)
        self.database_connection.send(command, zmq.SNDMORE)
        self.database_connection.send_pyobj(data_to_track, zmq.SNDMORE)
        self.database_connection.send(str(self.idn), zmq.SNDMORE)
        self.database_connection.send(self.group, zmq.SNDMORE)
        self.database_connection.send(str(self.round))

    def __reject_polled_but_not_accepted_offers(self):
        to_reject = []
        for offer_id in self._open_offers:
            if self._open_offers[offer_id]['status'] == 'polled':
                to_reject.append(offer_id)
            elif self._open_offers[offer_id]['status'] == 'received':
                good = self._open_offers[offer_id]['good']
        for offer_id in to_reject:
            self.reject(self._open_offers[offer_id])

    def aesof_exec(self, column_name):
        """ executes a command in your excel file. see instruction of pythons exec commmand """
        try:
            exec(self.aesof[column_name], globals(), locals())
            del self.aesof[column_name]
        except KeyError:
            pass

    def aesof_eval(self, column_name):
        """ evaluates an expression' in your excel file. see instruction of pythons eval commmand """
        return eval(self.aesof[column_name], globals(), locals())

    def _aesof(self):
        self.aesof = self.commands.recv_pyobj()

    #TODO go to trade
    def _clearing__end_of_subround(self):
        """ agent receives all messages and objects that have been send in this
        subround and deletes the offers that where retracted, but not executed.

        '_o': registers a new offer
        '_d': delete received that the issuing agent retract
        '_a': clears a made offer that was accepted by the other agent
        '_p': counterparty partially accepted a given offer
        '_r': deletes an offer that the other agent rejected
        '_g': recive a 'free' good from another party
        """
        while True:
            typ = self.messages_in.recv()
            if typ == '.':
                break
            msg = self.messages_in.recv_pyobj()
            if   typ == '_o':
                msg['status'] = 'received'
                self._open_offers[msg['idn']] = msg
                #TODO make self._open_offers a pointer to _msgs['_o']
                #TODO make different lists for sell and buy offers
            elif typ == '_d':
                del self._open_offers[msg]
            elif typ == '_a':
                offer = self._receive_accept(msg)
                self._log_receive_accept(offer)
            elif typ == '_p':
                offer = self._receive_partial_accept(msg)
                self._log_receive_partial_accept(offer)
            elif typ == '_r':
                self._receive_reject(msg)
            elif typ == '_g':
                self._haves[msg[0]] += msg[1]
            elif typ == '_q':
                self._quotes[msg['idn']] = msg
            else:
                self._msgs.setdefault(typ, []).append(Message(msg))

        while True:
            address = self.shout.recv()
            if address == 'all.':
                break
            typ = self.shout.recv()
            msg = self.shout.recv_pyobj()
            self._msgs.setdefault(typ, []).append(Message(msg))


    def __signal_finished(self):
        """ signals modelswarm via communication that the agent has send all
        messages and finish his action """
        self.out.send_multipart(['!', '.'])

    def _send(self, receiver_group, receiver_idn, typ, msg):
        """ sends a message to 'receiver_group', who can be an agent, a group or
        'all'. The agents receives it at the begin of each round in
        self.messages(typ) is 'm' for mails.
        typ =(_o,c,u,r) are
        reserved for internally processed offers.
        """
        self.out.send('%s_%i:' % (receiver_group.encode('ascii'), receiver_idn), zmq.SNDMORE)
        self.out.send(typ, zmq.SNDMORE)
        self.out.send_pyobj(msg)

    def _send_to_group(self, receiver_group, typ, msg):
        """ sends a message to 'receiver_group', who can be an agent, a group or
        'all'. The agents receives it at the begin of each round in
        self.messages(typ) is 'm' for mails.
        typ =(_o,c,u,r) are
        reserved for internally processed offers.
        """
        self.out.send('!', zmq.SNDMORE)
        self.out.send('s', zmq.SNDMORE)
        self.out.send('%s:' % receiver_group.encode('ascii'), zmq.SNDMORE)
        self.out.send(typ, zmq.SNDMORE)
        self.out.send_pyobj(msg)


def flatten(d, parent_key=''):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s_' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)
