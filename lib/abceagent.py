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
from abcetools import *
from inspect import getmembers, ismethod
from random import shuffle
save_err = np.seterr(invalid='ignore')


class Messaging:
    def message(self, receiver_group, receiver_idn, topic, content):
        """ sends a message to agent. Agents receive it
        at the beginning of next round with :meth:`~abceagent.Messaging.get_messages` or
        :meth:`~abceagent.Messaging.get_messages_all`.

        See:
            message_to_group for messages to multiple agents

        Args::

         receiver_group: agent, agent_group or 'all'
         topic: string, with which this message can be received
         content: string, dictionary or class, that is send.

        Example::

            ... household_01 ...
            self.message('firm', 01, 'quote_sell', {'good':'BRD', 'quantity': 5})

            ... firm_01 - one subround later ...
            requests = self.get_messages('quote_sell')
            for req in requests:
                self.sell(req.sender, req.good, reg.quantity, self.price[req.good])

        Example2::

         self.message('firm', 01, 'm', "hello my message")

        """
        msg = message(self.group, self.idn, receiver_group, receiver_idn, topic, content)
        self._send(receiver_group, receiver_idn, topic, msg)

    def message_to_group(self, receiver_group, topic, content):
        """ sends a message to agent, agent_group or 'all'. Agents receive it
        at the beginning of next round with :meth:`~abceagent.Messaging.get_messages` or
        :meth:`~abceagent.Messaging.get_messages_all`.

        Args::

         receiver_group: agent, agent_group or 'all'
         topic: string, with which this message can be received
         content: string, dictionary or class, that is send.

        Example::

            ... household_01 ...
            self.message('firm_01', 'quote_sell', {'good':'BRD', 'quantity': 5})

            ... firm_01 - one subround later ...
            requests = self.get_messages('quote_sell')
            for req in requests:
                self.sell(req.sender, req.good, reg.quantity, self.price[req.good])

        Example2::

         self.message('firm_01', 'm', "hello my message")

        """
        msg = message(self.group, self.idn, receiver_group, None, topic, content)
        self._send_to_group(receiver_group, topic, msg)


    def get_messages(self, topic='m'):
        """ returns all new messages send with :meth:`~abceagent.Messaging.message`
        (topic='m'). The order is randomized. self.messages(topic) returns all
        messages with a topic.

        A message is a string with the message. You can also retrieve the sender
        by `message.sender_group` and `message.sender_idn` and view the topic with
        'message.topic'. (see example)

        If you are sending a float or an integer you need to access the message
        content with `message.content` instead of only `message`.

        Example::

         ... agent_01 ...
         self.messages('firm_01', 'potential_buyers', 'hello message')

         ... firm_01 - one subround later ...
         potential_buyers = get_messages('potential_buyers')
         for msg in potential_buyers:
            print('message: ', msg)
            print('message: ', msg.content)
            print('group name: ', msg.sender_group)
            print('sender id: ', msg.sender_idn)
            print('topic: ', msg.topic)

        """
        try:
            shuffle(self._msgs[topic])
        except KeyError:
            self._msgs[topic] = []
        return self._msgs.pop(topic)

    def get_messages_all(self):
        """ returns all messages irregardless of the topic, in a dictionary by topic

        A message is a string with the message. You can also retrieve the sender
        by `message.sender_group` and `message.sender_idn` and view the topic with
        'message.topic'. (see example)

        If you are sending a float or an integer you need to access the message
        content with `message.content` instead of only `message`.
        """
        ret = self._msgs
        self._msgs = {}
        return ret

    def get_messages_biased(self, topic='m'):
        """ like self.messages(topic), but the order is not properly randomized, but
        its faster. use whenever you are sure that the way you process messages
        is not affected by the order
        """
        try:
            return self._msgs.pop(topic)
        except KeyError:
            return []


def message(sender_group, sender_idn, receiver_group, receiver_idn, topic, content):
    msg = {}
    msg['sender_group'] = sender_group
    msg['sender_idn'] = sender_idn
    msg['receiver_group'] = receiver_group
    msg['receiver_idn'] = receiver_idn
    msg['topic'] = topic
    msg['content'] = content
    return msg


class Message():
    def __init__(self, msg):
        self.__dict__ = msg

    def __get__(self):
        return self.content

    def __str__(self):
        return str(self.content)

    def __getitem__(self, key):
        return self.content[key]


class Trade:
    """ Agents can trade with each other. The clearing of the trade is taken care
    of fully by ABCE.
    Selling a good works in the following way:

    1. An agent sends an offer. :meth:`~abceagent.Trade.sell`

       *The good offered is blocked and self.possession(...) does not account for it.*

    2. **Next subround:** An agent receives the offer :meth:`~abceagent.Trade.get_offers`, and can
       :meth:`~abceagent.Trade.accept`, :meth:`~abceagent.Trade.reject` or partially accept it. :meth:`~abceagent.Trade.accept_partial`

       *The good is credited and the price is deducted from the agent's possesions.*

    3. **Next subround:**

       - in case of acceptal *the money is automatically credited.*
       - in case of partial acceptance *the money is credited and part of the blocked good is unblocked.*
       - in case of rejection *the good is unblocked.*

    Analogously for buying. (:meth:`~buy`)

    Example::

        # Agent 1
        def sales(self):
            self.remember_trade = self.sell('Household', 0, 'cookies', quantity=5, price=self.price)

        # Agent 2
        def receive_sale(self):
            oo = self.get_offers('cookies')
            for offer in oo:
                if offer['price'] < 0.3:
                    try:
                        self.accept(offer)
                    except NotEnoughGoods:
                        self.accept_partial(offer, self.possession('money') / offer['price'])
                else:
                    self.reject(offer)

        # Agent 1, subround 3
        def learning(self):
            offer = self.info(self.remember_trade)
            if offer['status'] == 'reject':
                self.price *= .9
            elif offer['status'] = 'partial':
                self.price *= offer['final_quantity'] / offer['quantity']

    Quotes on the other hand allow you to ask a trade partner to send you a not committed price quote.
    The modeller has to implement a response mechanism. For convenience :meth:`~abceagent.Trade.accept_quote` and
    :meth:`~abceagent.Trade.accept_quote_partial`, send a committed offer that its the uncommitted price quote.


    """
    def get_quotes(self):
        """ self.quotes() returns all new quotes and removes them. The order
        is randomized.

        Example::

         quotes = self.get_quotes()

        Returns::
         list of quotes
        """
        if 'q' not in self._msgs:
            return []
        shuffle(self._msgs['q'])
        return self._msgs.pop('q')

    def get_quotes_biased(self):
        """ like self.quotes(), but the order is not randomized, so
        its faster.

        self.quotes() returns all new quotes and removes them. The order
        is randomized.

        Use whenever you are sure that the way you process messages
        is not affected by the order.
        """
        if 'q' in self._msgs:
            return self._msgs.pop('q')
        else:
            return []

    def info(self, offer_idn):
        """ lets you access all fields of a **given** offer.
        This allows you to check whether an offer was accepted, partially accepted
        or rejected and retrieve the quantity actually traded.

        If in your first round the value your are testing is not set, set the variable
        to `None`. None in the first round returns an empty trade with quantity = 0 and price = 1.
        The status in accepted.

        Example::

            class Example:
                def __init__(self):
                    self.last_offer = None
                    self.price = 5

                def selling(self):
                    if self.info(self.last_offer)['status'] == 'accept':
                        self.price += 1
                    self.last_offer = self.sell('Household', 1, 'cookies', 5, self.price)

        Returns a dictionary; Fields:
            ['status']:
                'accepted':
                    trade fully accepted
                'partial':
                    ['final_quantity'] and self.offer_partial_status_percentage(...)
                    for the quantities actually accepted
                'rejected':
                    trade rejected
                'perished':
                    the **perishable** good was not accepted by the end of the round
                    and therefore perished.
            ['quantity']:
                the quantity of the original quote.
            ['final_quantity']:
                This returns the accutal quantity bought or sold. (Equal to quantity
                    if the offer was accepted fully)

        Raises:
            KeyError:
                If the offer was answered more than one round ago.
            KeyError - Dictionary:
                The dictionary has no status and raises a KeyError, iff the offer
                was not yet answered.
                see `Example Pending` below.


        Example Pending::

            try:
                status = info(self.offer_idn)['status']
            except KeyError:
                print('offer has not yet been answered')

        Example::

            from pybrain.rl.learners.valuebased import ActionValueTable
            from pybrain.rl.agents import LearningAgent
            from pybrain.rl.learners import Q

            def __init__(self):
                controller = ActionValueTable(dimState=1, numActions=1)
                learner = Q()
                rl_price = LearningAgent(controller, learner)
                self.car_cost = 500

            def sales(self):
                price = reinforcement_learner.getAction():
                self.offer = self.sell('Household', 1, 'car', 1, price)

            def learn(self):
                reinforcement_learner.integrateObservation([offer_status(self.offer)])
                reinforcement_learner.giveReward([offer_status(self.offer) * price - self.car_cost])
        """
        offer = self.given_offers[offer_idn]
        if offer['status'] == 'accepted':
            offer['final_quantity'] = offer['quantity']
        elif  offer['status'] == 'rejected':
            offer['final_quantity'] = 0
        return offer

    def partial_status_percentage(self, offer_idn):
        """ returns the percentage of a partial accept

        Args:
            offer_idn:
                on offer as returned by self.sell(...) ord self.buy(...)

        Returns:
            A value between [0, 1]

        Raises:
            KeyError, when no answer has not been given or received more than one round before
        """
        try:
            return (self.given_offers[offer_idn]['final_quantity'] /
                            self.given_offers[offer_idn]['quantity'])
        except KeyError:
            if self.given_offers[offer_idn]['status'] == 'accepted':
                return 1
            elif self.given_offers[offer_idn]['status'] == 'rejected':
                return 0
            else:
                raise KeyError


    def accept_quote(self, quote):
        """ makes a commited buy or sell out of the counterparties quote

        Args::
         quote: buy or sell quote that is accepted

        """
        if quote['buysell'] == 'qs':
            self.buy(quote['sender'], quote['good'], quote['quantity'], quote['price'])
        else:
            self.sell(quote['sender'], quote['good'], quote['quantity'], quote['price'])

    def accept_quote_partial(self, quote, quantity):
        """ makes a commited buy or sell out of the counterparties quote

        Args::
         quote: buy or sell quote that is accepted
         quantity: the quantity that is offered/requested
         it should be less than propsed in the quote, but this is not enforced.

        """
        if quote['buysell'] == 'qs':
            self.buy(quote['sender'], quote['good'], quantity, quote['price'])
        else:
            self.sell(quote['sender'], quote['good'], quantity, quote['price'])

    #TODO create assert unanswered offers

    def get_offers_all(self, descending=False):
        """ returns all offers in a dictionary, with goods as key. The in each
        goods-category the goods are ordert by price. The order can be reverse
        by setting descending=True

        *Offers that are not accepted in the same subround (def block) are
        automatically rejected.* However you can also manualy reject.

        Args::

         descending(optional): is a bool. False for descending True for
                               ascending by price

        Example2::

         oo = get_offers_all(descending=False)
         for good_category in oo:
            print('The cheapest good of category' + good_category
            + ' is ' + good_category[0])
         #sorted list of beer prices and seller
         for offer in oo['beer']:
            print(offer['price'], offer['sender'])

        Lists can only efficiently pop the last item. Therefore it is more
        efficient to order backward and buy the last good first::

         def buy_input_good(self):
            offers = self.get_offers_all(descending=True)
            while offers:
                if offers[good][-1]['quantity'] == self.prices_for_which_buy[good]:
                    self.accept(offers[good].pop())
        """
        offers_by_good = defaultdict(list)
        for offer_id in self._open_offers:
            self._open_offers[offer_id]['status'] = 'polled'
            offer = self._open_offers[offer_id]
            offers_by_good[offer['good']].append(offer)
        for key in offers_by_good:
            shuffle(offers_by_good[key])
            offers_by_good[key].sort(key=lambda objects: objects['price'], reverse=descending)
        return offers_by_good

    def get_offers(self, good, descending=False):
        """ returns all offers of the 'good' ordered by price.

        *Offers that are not accepted in the same subround (def block) are
        automatically rejected.* However you can also manualy reject.

        Args::

         good: the good which should be retrieved
         descending(=False): is a bool. False for descending True for
                             ascending by price

        Example::

            offers = get_offers('books')
            for offer in offers:
                if offer['price'] < 50:
                    self.accept(offer)
                elif offer['price'] < 100:
                    self.accept_partial(offer, 1)
                else:
                    self.reject(offer)  # optional
        """
        ret = []
        for offer_idn in self._open_offers:
            if self._open_offers[offer_idn]['good'] == good:
                self._open_offers[offer_idn]['status'] = 'polled'
                ret.append(self._open_offers[offer_idn])
        shuffle(ret)
        ret.sort(key=lambda objects: objects['price'], reverse=descending)
        return ret

    def quote_sell(self, receiver_group, receiver_idn, good, quantity, price):
        """ quotes a price to sell quantity of 'good' to a receiver

        price (money) per unit
        offers a deal without checking or committing resources

        Args:
            receiver_group:
                agent group name of the agent
            receiver_idn:
                the agent's id number
            'good':
                name of the good
            quantity:
                maximum units disposed to sell at this price
            price:
                price per unit
        """
        offer = Offer(self.group, self.idn, receiver_group, receiver_idn, good, quantity, price, 'qs')
        self._send(receiver_group, receiver_idn, 'q', offer)
        return offer

    def quote_buy(self, receiver_group, receiver_idn, good, quantity, price):
        """ quotes a price to buy quantity of 'good' a receiver

        price (money) per unit
        offers a deal without checking or committing resources

        Args:
            receiver_group:
                agent group name of the agent
            receiver_idn:
                the agent's id number
            'good':
                name of the good
            quantity:
                maximum units disposed to buy at this price
            price:
                price per unit
        """
        offer = Offer(self.group, self.idn, receiver_group, receiver_idn, good, quantity, price, 'qb')
        self._send(receiver_group, receiver_idn, 'q', offer)
        return offer

    def sell(self, receiver_group, receiver_idn, good, quantity, price):
        """ commits to sell the quantity of good at price

        The goods are not in haves or self.count(). When the offer is
        rejected they are automatically reacreditated. When the offer is
        accepted the money amount is accreditated. (partial acceptance
        accordingly)

        Args:
            receiver_group: an agent name  NEVER a group or 'all'!!!
            (its an error but with a confusing warning)
            'good': name of the good
            quantity: maximum units disposed to buy at this price
            price: price per unit

        Returns:
            A reference to the offer. The offer and the offer status can
            be accessed with `self.info(offer_reference)`.

        Example::

            def subround_1(self):
                self.offer = self.sell('household', 1, 'cookies', quantity=5, price=0.1)

            def subround_2(self):
                offer = self.info(self.offer)
                if offer['status'] == 'partial':
                    print(offer['final_quantity'] , 'cookies have be bougth')
                elif:
                    offer['status'] == 'accepted':
                    print('Cookie monster bougth them all')
                elif:
                    offer['status'] == 'rejected':
                    print('On diet')
        """
        assert price >= - epsilon, price
        assert quantity > - epsilon, quantity
        if self._haves[good] < quantity - epsilon:
            raise NotEnoughGoods(self.name, good, quantity - self._haves[good])
        self._haves[good] -= quantity
        offer = Offer(self.group, self.idn, receiver_group, receiver_idn, good, quantity, price, buysell='s', idn=self._offer_counter())
        self._send(receiver_group, receiver_idn, '_o', offer)
        self.given_offers[offer['idn']] = offer
        return offer['idn']

    def buy(self, receiver_group, receiver_idn, good, quantity, price):
        """ commits to sell the quantity of good at price

        The goods are not in haves or self.count(). When the offer is
        rejected they are automatically reacreditated. When the offer is
        accepted the money amount is accreditated. (partial acceptance
        accordingly)

        Args:
            receiver_group: an agent name  NEVER a group or 'all'!!!
            (its an error but with a confusing warning)
            'good': name of the good
            quantity: maximum units disposed to buy at this price
            price: price per unit
        """
        money_amount = quantity * price
        if self._haves['money'] < money_amount - epsilon:
            raise NotEnoughGoods(self.name, 'money', money_amount - self._haves['money'])

        self._haves['money'] -= money_amount
        offer = Offer(self.group, self.idn, receiver_group, receiver_idn, good, quantity, price, 'b', self._offer_counter())
        self._send(receiver_group, receiver_idn, '_o', offer)
        self.given_offers[offer['idn']] = offer
        return offer['idn']

    def retract(self, offer_idn):
        """ The agent who made a buy or sell offer can retract it

        The offer an agent made is deleted at the end of the subround and the
        committeg good reapears in the haves. However if another agent
        accepts in the same round the trade will be cleared and not retracted.

        Args:
            offer: the offer he made with buy or sell
            (offer not quote!)
        """
        self._send(self.given_offers[offer_idn]['receiver_group'], '_d', offer['idn'])
        del self.given_offers[offer_idn]

    def accept(self, offer):
        """ The offer is accepted and cleared

        Args::

            offer: the offer the other party made
            (offer not quote!)

        Return:
            Returns a dictionary with the good's quantity and the amount paid.
        """
        money_amount = offer['quantity'] * offer['price']
        if offer['buysell'] == 's':
            if self._haves['money'] < money_amount - epsilon:
                raise NotEnoughGoods(self.name, 'money', money_amount - self._haves['money'])
            self._haves[offer['good']] += offer['quantity']
            self._haves['money'] -= offer['quantity'] * offer['price']
        else:
            if self._haves[offer['good']] < offer['quantity'] - epsilon:
                raise NotEnoughGoods(self.name, offer['good'], offer['quantity'] - self._haves[offer['good']])
            self._haves[offer['good']] -= offer['quantity']
            self._haves['money'] += offer['quantity'] * offer['price']
        self._send(offer['sender_group'], offer['sender_idn'], '_a', offer['idn'])
        del self._open_offers[offer['idn']]
        return {offer['good']: offer['quantity'], 'money': money_amount}

    def accept_partial(self, offer, quantity):
        """ TODO The offer is partly accepted and cleared

        Args:
            offer: the offer the other party made
            (offer not quote!)

        Return:
            Returns a dictionary with the good's quantity and the amount paid.
        """
        assert not(is_negative(quantity)), quantity
        assert quantity <= offer['quantity'], 'accepted more than offered %s: %f > %s' % (offer['good'], quantity, offer['quantity'])
        money_amount = quantity * offer['price']
        if offer['buysell'] == 's':
            if self._haves['money'] < money_amount - epsilon:
                raise NotEnoughGoods(self.name, 'money', money_amount - self._haves['money'])
            self._haves[offer['good']] += quantity
            self._haves['money'] -= quantity * offer['price']
        else:
            if self._haves[offer['good']] < quantity - epsilon:
                raise NotEnoughGoods(self.name, offer['good'], quantity - self._haves[offer['good']])
            self._haves[offer['good']] -= quantity
            self._haves['money'] += quantity * offer['price']
        offer['final_quantity'] = quantity
        self._send(offer['sender_group'], offer['sender_idn'], '_p', offer)
        del self._open_offers[offer['idn']]
        return {offer['good']: quantity, 'money': money_amount}

    def reject(self, offer):
        """ The offer is rejected

        Args:
            offer: the offer the other party made
            (offer not quote!)
        """
        self._send(offer['sender_group'], offer['sender_idn'], '_r', offer['idn'])
        del self._open_offers[offer['idn']]

    def _receive_accept(self, offer_id):
        """ When the other party accepted the  money or good is received
        and the offer deleted
        """
        offer = self.given_offers[offer_id]
        if offer['buysell'] == 's':
            self._haves['money'] += offer['quantity'] * offer['price']
        else:
            self._haves[offer['good']] += offer['quantity']
        offer['status'] = "accepted"
        offer['status_round'] = self.round
        self.given_offers[offer_id] = offer
        return offer

    def _log_receive_accept_group(self, offer):
        if offer['buysell'] == 's':
            self._trade_log['%s,%s,%s,%f' % (offer['good'], self.group, offer['receiver_group'], offer['price'])] += offer['quantity']
        else:
            self._trade_log['%s,%s,%s,%f' % (offer['good'], offer['receiver_group'], self.group, offer['price'])] += offer['quantity']

    def _log_receive_accept_agent(self, offer):
        if offer['buysell'] == 's':
            self._trade_log['%s,%s,%s,%f' % (offer['good'], self.name, agent_name(offer['receiver_group'], offer['receiver_idn']), offer['price'])] += offer['quantity']
        else:
            self._trade_log['%s,%s,%s,%f' % (offer['good'], agent_name(offer['receiver_group'], offer['receiver_idn']), self.name, offer['price'])] += offer['quantity']

    def _receive_partial_accept(self, offer):
        """ When the other party partially accepted the  money or good is
        received, remaining good or money is added back to haves and the offer
        is deleted
        """
        if offer['buysell'] == 's':
            self._haves['money'] += offer['final_quantity'] * offer['price']
            self._haves[offer['good']] += offer['quantity'] - offer['final_quantity']
        else:
            self._haves[offer['good']] += offer['final_quantity']
            self._haves['money'] += (offer['quantity'] - offer['final_quantity']) * offer['price']
        offer['status'] = "partial"
        offer['status_round'] = self.round
        self.given_offers[offer['idn']] = offer
        return offer

    def _log_receive_partial_accept_group(self, offer):
        if offer['buysell'] == 's':
            self._trade_log['%s,%s,%s,%f' % (offer['good'], self.group, offer['receiver_group'], offer['price'])] += offer['final_quantity']
        else:
            self._trade_log['%s,%s,%s,%f' % (offer['good'], offer['receiver_group'], self.group, offer['price'])] += offer['final_quantity']

    def _log_receive_partial_accept_agent(self, offer):
        if offer['buysell'] == 's':
            self._trade_log['%s,%s,%s,%f' % (offer['good'], self.name, agent_name(offer['receiver_group'], offer['receiver_idn']), offer['price'])] += offer['final_quantity']
        else:
            self._trade_log['%s,%s,%s,%f' % (offer['good'], agent_name(offer['receiver_group'], offer['receiver_idn']), self.name, offer['price'])] += offer['final_quantity']

    def _receive_reject(self, offer_id):
        """ delets a given offer

        is used by _msg_clearing__end_of_subround, when the other party rejects
        or at the end of the subround when agent retracted the offer

        """
        offer = self.given_offers[offer_id]
        if offer['buysell'] == 's':
            self._haves[offer['good']] += offer['quantity']
        else:
            self._haves['money'] += offer['quantity'] * offer['price']
        offer['status'] = "rejected"
        offer['status_round'] = self.round
        self.given_offers[offer_id] = offer

    def _delete_given_offer(self, offer_id):
        offer = self.given_offers.pop(offer_id)
        if offer['buysell'] == 's':
            self._haves[offer['good']] += offer['quantity']
        else:
            self._haves['money'] += offer['quantity'] * offer['price']

    def give(self, receiver_group, receiver_idn, good, quantity):
        """ gives a good to another agent

        Args:

            receiver_group:
                Group name of the receiver
            receiver_idn:
                id number of the receiver
            good:
                the good to be transfered
            quantity:
                amount to be transfered

        Raises:

            AssertionError, when good smaller than 0.

        Return:
            Dictionary, with the transfere, which can be used by self.log(...).

        Example::

            self.log('taxes', self.give('money': 0.05 * self.possession('money'))

        """
        assert quantity >= 0
        if self._haves[good] < quantity - epsilon:
            raise NotEnoughGoods(self.name, good, quantity - self._haves[good])
        self._haves[good] -= quantity
        self._send(receiver_group, receiver_idn, '_g', [good, quantity])
        return {good: quantity}

    #TODO take


class FirmMultiTechnologies:
    def produce_use_everything(self, production_function):
        """ Produces output goods from all input goods, used in this
        production_function, the agent owns.

        Args::

            production_function: A production_function produced with
            py:meth:`~abceagent.FirmMultiTechnologies.create_production_function`, py:meth:`~abceagent.FirmMultiTechnologies.create_cobb_douglas` or
            py:meth:`~abceagent.FirmMultiTechnologies.create_leontief`

        Example::

            self.produce_use_everything(car_production_function)
        """
        return self.produce(production_function, dict((inp, self.possession(inp)) for inp in production_function['input']))

    def produce(self, production_function, input_goods):
        """ Produces output goods given the specified amount of inputs.

        Transforms the Agent's goods specified in input goods
        according to a given production_function to output goods.
        Automatically changes the agent's belonging. Raises an
        exception, when the agent does not have sufficient resources.

        Args:
            production_function:
                A production_function produced with py:meth:`~abceagent.FirmMultiTechnologies..create_production_function`,
                py:meth:`~abceagent.FirmMultiTechnologies..create_cobb_douglas` or py:meth:`~abceagent.FirmMultiTechnologies..create_leontief`
            input goods {dictionary}:
                dictionary containing the amount of input good used for the production.

        Raises:
            NotEnoughGoods: This is raised when the goods are insufficient.

        Example::

            car = {'tire': 4, 'metal': 2000, 'plastic':  40}
            bike = {'tire': 2, 'metal': 400, 'plastic':  20}
            try:
                self.produce(car_production_function, car)
            except NotEnoughGoods:
                A.produce(bike_production_function, bike)
        """
        for good in production_function['input']:
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(self.name, good, (input_goods[good] - self._haves[good]))
        for good in production_function['input']:
            self._haves[good] -= input_goods[good]
        goods_vector = dict((good, 0) for good in production_function['output'])
        goods_vector.update(input_goods)
        exec(production_function['code'], {}, goods_vector)
        for good in production_function['output']:
            self._haves[good] += goods_vector[good]
        return dict([(good, goods_vector[good]) for good in production_function['output']])

    def create_production_function(self, formula, typ='from_formula'):
        """ creates a production function from formula

        A production function is a produceation process that produces the
        given input given input goods according to the formula to the output
        goods.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        create_production_function_fast is faster but more complicated

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are seperated by a ;

        Returns:
            A production_function that can be used in produce etc.

        Example:
            formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
            self.production_function = self.create_production_function(formula)
            self.produce(self.production_function, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        parse_single_output = pp.Word(pp.alphas + "_", pp.alphanums + "_") + pp.Suppress('=') + pp.Suppress(pp.Word(pp.alphanums + '*/+-().[]{} '))
        parse_output = pp.delimitedList(parse_single_output, ';')
        parse_single_input = pp.Suppress(pp.Word(pp.alphas + "_", pp.alphanums + "_")) + pp.Suppress('=') \
                + pp.OneOrMore(pp.Suppress(pp.Optional(pp.Word(pp.nums + '*/+-().[]{} '))) + pp.Word(pp.alphas + "_", pp.alphanums + "_"))
        parse_input = pp.delimitedList(parse_single_input, ';')

        production_function = {}
        production_function['type'] = typ
        production_function['formula'] = formula
        production_function['code'] = compiler.compile(formula, '<string>', 'exec')
        production_function['output'] = list(parse_output.parseString(formula))
        production_function['input'] = list(parse_input.parseString(formula))
        return production_function

    def create_production_function_fast(self, formula, output_goods, input_goods, typ='from_formula'):
        """ creates a production function from formula, with given outputs

        A production function is a producetion process that produces the
        given input given input goods according to the formula to the output
        goods.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are seperated by a ;
            [output]: list of all output goods (left hand sides of the equations)

        Returns:
            A production_function that can be used in produce etc.

        Example:
            formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
            self.production_function = self.create_production_function(formula, 'golf', ['waste', 'paint'])
            self.produce(self.production_function, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        production_function = {}
        production_function['type'] = typ
        production_function['formula'] = formula
        production_function['code'] = compiler.compile(formula, '<string>', 'exec')
        production_function['output'] = output_goods
        production_function['input'] = input_goods
        return production_function

    def create_cobb_douglas(self, output, multiplier, exponents):
        """ creates a Cobb-Douglas production function

        A production function is a production process that produces the
        given input given input goods according to the formula to the output
        good.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Args:
            'output': Name of the output good
            multiplier: Cobb-Douglas multiplier
            {'input1': exponent1, 'input2': exponent2 ...}: dictionary
            containing good names 'input' and correstponding exponents
        Returns:
            A production_function that can be used in produce etc.

        Example:
        self.plastic_production_function = self.create_cobb_douglas('plastic', {'oil' : 10, 'labor' : 1}, 0.000001)
        self.produce(self.plastic_production_function, {'oil' : 20, 'labor' : 1})

        """
        ordered_input = [input_good for input_good in exponents]
        formula = output + '=' + str(multiplier) + '*' + '*'.join('(%s)**%f' % (input_good, exponent) for input_good, exponent in exponents.iteritems())
        optimization = '*'.join(['(%s)**%f' % ('%s', exponents[good]) for good in ordered_input])
        production_function = {}
        production_function['type'] = 'cobb-douglas'
        production_function['parameters'] = exponents
        production_function['formula'] = formula
        production_function['multiplier'] = multiplier
        production_function['code'] = compiler.compile(formula, '<string>', 'exec')
        production_function['output'] = [output]
        production_function['input'] = ordered_input
        production_function['optimization'] = optimization
        return production_function


    def create_leontief(self, output, utilization_quantities, isinteger=''):
        """ creates a Leontief production function


        A production function is a produceation process that produces the
        given input given input goods according to the formula to the output
        good.
        Production_functions are than used as an argument in produce,
        predict_vector_produce and predict_output_produce.

        Warning, when you produce with a Leontief production_function all goods you
        put in the produce(...) function are used up. Regardless whether it is an
        efficient or wastefull bundle

        Args:
            'output':
                Name of the output good
            utilization_quantities:
                a dictionary containing good names and correstponding exponents
            isinteger='int' or isinteger='':
                When 'int' produce only integer amounts of the good.
                When '', produces floating amounts. (default)

        Returns:
            A production_function that can be used in produce etc.

        Example:
        self.car_technology = self.create_leontief('car', {'tire' : 4, 'metal' : 1000, 'plastic' : 20}, 1)
        two_cars = {'tire': 8, 'metal': 2000, 'plastic':  40}
        self.produce(self.car_technology, two_cars)
        """
        uqi = utilization_quantities.iteritems()
        ordered_input = [input_good for input_good in utilization_quantities]
        coefficients = ','.join('%s/%f' % (input_good, input_quantity) for input_good, input_quantity in uqi)
        formula = output + ' = ' + isinteger + '(min([' + coefficients + ']))'
        opt_coefficients = ','.join('%s/%f' % ('%s', utilization_quantities[good]) for good in ordered_input)
        optimization = isinteger + '(min([' + opt_coefficients + ']))'
        production_function = {}
        production_function['type'] = 'leontief'
        production_function['parameters'] = utilization_quantities
        production_function['formula'] = formula
        production_function['isinteger'] = isinteger
        production_function['code'] = compiler.compile(formula, '<string>', 'exec')
        production_function['output'] = [output]
        production_function['input'] = ordered_input
        production_function['optimization'] = optimization
        return production_function

    def predict_produce_output(self, production_function, input_goods):
        """ Predicts the output of a certain input vector and for a given
            production function

            Predicts the production of produce(production_function, input_goods)
            see also: Predict_produce(.) as it returns a calculatable vector

        Args::

            production_function: A production_function produced with
            create_production_function, create_cobb_douglas or create_leontief
            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good used for the production.

        Returns::

            A dictionary of the predicted output


        Example::

            print(A.predict_output_produce(car_production_function, two_cars))
            >>> {'car': 2}

        """
        goods_vector = input_goods.copy()
        for good in production_function['output']:
            goods_vector[good] = None
        exec(production_function['code'], {}, goods_vector)
        output = {}
        for good in production_function['output']:
            output[good] = goods_vector[good]
        return output


    def predict_produce(self, production_function, input_goods):
        """ Returns a vector with input (negative) and output (positive) goods

            Predicts the production of produce(production_function, input_goods) and
            the use of input goods.
            net_value(.) uses a price_vector (dictionary) to calculate the
            net value of this production.

        Args:
            production_function: A production_function produced with
            create_production_function, create_cobb_douglas or create_leontief
            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good used for the production.

        Example::

         prices = {'car': 50000, 'tire': 100, 'metal': 10, 'plastic':  0.5}
         value_one_car = net_value(predict_produce(car_production_function, one_car), prices)
         value_two_cars = net_value(predict_produce(car_production_function, two_cars), prices)
         if value_one_car > value_two_cars:
            A.produce(car_production_function, one_car)
         else:
            A.produce(car_production_function, two_cars)
        """
        goods_vector = input_goods.copy()
        result = defaultdict(int)
        for good in production_function['output']:
            goods_vector[good] = None
        exec(production_function['code'], {}, goods_vector)
        for goods in production_function['output']:
            result[good] = goods_vector[good]
        for goods in production_function['input']:
            result[good] = -goods_vector[good]
        return result


    def net_value(self, goods_vector, price_vector):
        """ Calculates the net_value of a goods_vector given a price_vector

            goods_vectors are vector, where the input goods are negative and
            the output goods are positive. When we multiply every good with its
            according price we can calculate the net_value of the correstponding
            production.
            goods_vectors are produced by predict_produce(.)


        Args:
            goods_vector: a dictionary with goods and quantities
            e.G. {'car': 1, 'metal': -1200, 'tire': -4, 'plastic': -21}
            price_vector: a dictionary with goods and prices (see example)

        Example::

         prices = {'car': 50000, 'tire': 100, 'metal': 10, 'plastic':  0.5}
         value_one_car = net_value(predict_produce(car_production_function, one_car), prices)
         value_two_cars = net_value(predict_produce(car_production_function, two_cars), prices)
         if value_one_car > value_two_cars:
            produce(car_production_function, one_car)
         else:
            produce(car_production_function, two_cars)
        """
        ret = 0
        for good, quantity in goods_vector.items():
            ret += price_vector[good] * quantity
        return ret

    def sufficient_goods(self, input_goods):
        """ checks whether the agent has all the goods in the vector input """
        for good in input_goods:
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(self.name, good, input_goods[good] - self._haves[good])


class Firm(FirmMultiTechnologies):
    """ The firm class allows you to declare a production function for a firm.
    :meth:`~Firm.set_leontief`, :meth:`~abecagent.Firm.set_production_function`
    :meth:`~Firm.set_cobb_douglas`,
    :meth:`~Firm.set_production_function_fast`
    (FirmMultiTechnologies, allows you to declare several) With :meth:`~Firm.produce`
    and :meth:`~Firm.produce_use_everything` you can produce using the
    according production function. You have several auxiliarifunctions
    for example to predict the production. When you multiply
    :meth:`~Firm.predict_produce` with the price vector you get the
    profitability of the prodiction.
    """
    #TODO Example
    def produce_use_everything(self):
        """ Produces output goods from all input goods.

        Example::

            self.produce_use_everything()
        """
        return self.produce(self.possessions_all())

    def produce(self, input_goods):
        """ Produces output goods given the specified amount of inputs.

        Transforms the Agent's goods specified in input goods
        according to a given production_function to output goods.
        Automatically changes the agent's belonging. Raises an
        exception, when the agent does not have sufficient resources.

        Args:
            {'input_good1': amount1, 'input_good2': amount2 ...}:
                dictionary containing the amount of input good used for the production.

        Raises:
            NotEnoughGoods:
                This is raised when the goods are insufficient.

        Example::

            self.set_cobb_douglas_production_function('car' ..)
            car = {'tire': 4, 'metal': 2000, 'plastic':  40}
            try:
                self.produce(car)
            except NotEnoughGoods:
                print('today no cars')
        """
        return FirmMultiTechnologies.produce(self, self._production_function, input_goods)

    def sufficient_goods(self, input_goods):
        """ checks whether the agent has all the goods in the vector input """
        FirmMultiTechnologies.sufficient_goods(self)

    def set_production_function(self, formula, typ='from_formula'):
        """  sets the firm to use a Cobb-Douglas production function from a
        formula.

        A production function is a produceation process that produces the given
        input given input goods according to the formula to the output goods.
        Production_functions are than used to produce, predict_vector_produce and
        predict_output_produce.

        create_production_function_fast is faster but more complicated

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are seperated by a ;

        Example::

            formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
            self.set_production_function(formula)
            self.produce({'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        self._production_function = self.create_production_function(formula, typ)

    def set_production_function_fast(self, formula, output_goods, input_goods, typ='from_formula'):
        """  sets the firm to use a Cobb-Douglas production function from a
        formula, with given outputs

        A production function is a produceation process that produces the given
        input given input goods according to the formula to the output goods.
        Production_functions are than used to produce, predict_vector_produce and
        predict_output_produce.

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are seperated by a ;
            [output]: list of all output goods (left hand sides of the equations)

        Example::

            formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
            self.production_function_fast(formula, 'golf', ['waste'])
            self.produce(self, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        self._production_function = self.create_production_function_fast(formula, output_goods, input_goods, typ)

    def set_cobb_douglas(self, output, multiplier, exponents):
        """  sets the firm to use a Cobb-Douglas production function.

        A production function is a produceation process that produces the
        given input given input goods according to the formula to the output
        good.

        Args:
            'output': Name of the output good
            multiplier: Cobb-Douglas multiplier
            {'input1': exponent1, 'input2': exponent2 ...}: dictionary
            containing good names 'input' and correstponding exponents

        Example::

            self.create_cobb_douglas('plastic', 0.000001, {'oil' : 10, 'labor' : 1})
            self.produce({'oil' : 20, 'labor' : 1})

        """
        self._production_function = self.create_cobb_douglas(output, multiplier, exponents)

    def set_leontief(self, output, utilization_quantities, multiplier=1, isinteger='int'):
        """ sets the firm to use a Leontief production function.

        A production function is a production process that produces the
        given input given input goods according to the formula to the output
        good.

        Warning, when you produce with a Leontief production_function all goods you
        put in the produce(...) function are used up. Regardless whether it is an
        efficient or wastefull bundle

        Args:
            'output': Name of the output good
            {'input1': utilization_quantity1, 'input2': utilization_quantity2 ...}: dictionary
            containing good names 'input' and correstponding exponents
            multiplier: multipler
            isinteger='int' or isinteger='': When 'int' produce only integer
            amounts of the good. When '', produces floating amounts.

        Example::

            self.create_leontief('car', {'tire' : 4, 'metal' : 1000, 'plastic' : 20}, 1)
            two_cars = {'tire': 8, 'metal': 2000, 'plastic':  40}
            self.produce(two_cars)
        """
        self._production_function = self.create_leontief(output, utilization_quantities, multiplier, isinteger)

    def predict_produce_output(self, production_function, input_goods):
        """ Calculates the output of a production (but does not preduce)

            Predicts the production of produce(production_function, input_goods)
            see also: Predict_produce(.) as it returns a calculatable vector

        Args:
            production_function: A production_function produced with
            create_production_function, create_cobb_douglas or create_leontief
            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good used for the production.

        Example::

            print(A.predict_output_produce(car_production_function, two_cars))
            >>> {'car': 2}

        """
        return predict_produce_output(self._production_function, input_goods)

    def predict_produce(self, production_function, input_goods):
        """ Returns a vector with input (negative) and output (positive) goods

            Predicts the production of produce(production_function, input_goods) and
            the use of input goods.
            net_value(.) uses a price_vector (dictionary) to calculate the
            net value of this production.

        Args:
            production_function: A production_function produced with
            create_production_function, create_cobb_douglas or create_leontief
            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good used for the production.

        Example::

         prices = {'car': 50000, 'tire': 100, 'metal': 10, 'plastic':  0.5}
         value_one_car = net_value(predict_produce(car_production_function, one_car), prices)
         value_two_cars = net_value(predict_produce(car_production_function, two_cars), prices)
         if value_one_car > value_two_cars:
             A.produce(car_production_function, one_car)
         else:
             A.produce(car_production_function, two_cars)
        """
        return predict_produce(self._production_function, input_goods)


class Household:
    def utility_function(self):
        """ the utility function should be created with:
        set_cobb_douglas_utility_function,
        create_utility_function or
        create_utility_function_fast
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
        return self.consume(dict((inp, self._haves[inp]) for inp in self._utility_function['input']))

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
            A the utility a number. To log it see example.

        Example::

            self.consumption_set = {'car': 1, 'ball': 2000, 'bike':  2}
            self.consumption_set = {'car': 0, 'ball': 2500, 'bike':  20}
            try:
                utility = self.consume(utility_function, self.consumption_set)
            except NotEnoughGoods:
                utility = self.consume(utility_function, self.smaller_consumption_set)
            self.log('utility': {'u': utility})

        """
        for good in self._utility_function['input']:
            if self._haves[good] < input_goods[good] - epsilon:
                raise NotEnoughGoods(self.name, good, self._utility_function['input'][good] - self._haves[good])
        for good in self._utility_function['input']:
            self._haves[good] -= input_goods[good]
        goods_vector = input_goods.copy()
        goods_vector['utility'] = None
        exec(self._utility_function['code'], {}, goods_vector)
        return goods_vector['utility']

    def set_utility_function(self, formula, typ='from_formula'):
        """ creates a utility function from formula

        Utility_functions are than used as an argument in consume_with_utility,
        predict_utility and predict_utility_and_consumption.

        create_utility_function_fast is faster but more complicatedutility_function

        Args:
            "formula": equation or set of equations that describe the
            utility function. (string) needs to start with 'utility = ...'

        Returns:
            A utility_function

        Example:
            formula = 'utility = ball + paint'
            self._utility_function = self.create_utility_function(formula)
            self.consume_with_utility(self._utility_function, {'ball' : 1, 'paint' : 2})

        //exponential is ** not ^
        """
        parse_single_input = pp.Suppress(pp.Word(pp.alphas + "_", pp.alphanums + "_")) + pp.Suppress('=') \
                + pp.OneOrMore(pp.Suppress(pp.Optional(pp.Word(pp.nums + '*/+-().[]{} ')))
                + pp.Word(pp.alphas + "_", pp.alphanums + "_"))
        parse_input = pp.delimitedList(parse_single_input, ';')

        self._utility_function = {}
        self._utility_function['type'] = typ
        self._utility_function['formula'] = formula
        self._utility_function['code'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input'] = list(parse_input.parseString(formula))

    def set_utility_function_fast(self, formula, input_goods, typ='from_formula'):
        """ creates a utility function from formula

        Utility_functions are than used as an argument in consume_with_utility,
        predict_utility and predict_utility_and_consumption.

        create_utility_function_fast is faster but more complicated

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are seperated by a ;
            [output]: list of all output goods (left hand sides of the equations)

        Returns:
            A utility_function that can be used in produce etc.

        Example:
            formula = 'utility = ball + paint'

            self._utility_function = self.create_utility_function(formula, ['ball', 'paint'])
            self.consume_with_utility(self._utility_function, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        self._utility_function = {}
        self._utility_function['type'] = typ
        self._utility_function['formula'] = formula
        self._utility_function['code'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input'] = input_goods

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
        formula = 'utility=' + ('*'.join(['**'.join([input_good, str(input_quantity)]) for input_good, input_quantity in exponents.iteritems()]))
        self._utility_function = {}
        self._utility_function['type'] = 'cobb-douglas'
        self._utility_function['parameters'] = exponents
        self._utility_function['formula'] = formula
        self._utility_function['code'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input'] = exponents.keys()

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
        goods_vector = input_goods.copy()
        goods_vector['utility'] = None
        exec(self._utility_function['code'], {}, goods_vector)
        return goods_vector['utility']


def sort(objects, key='price', reverse=False):
    """ Sorts the object by the key

    Args::

     reverse=True for descending

    Example::

        quotes_by_price = sort(quotes, 'price')
        """
    return sorted(objects, key=lambda objects: objects[key], reverse=reverse)


class Database:
    """ The database class """
    def log(self, action_name, data_to_log):
        """ With log you can write the models data. Log can save variable states
        and and the working of individual functions such as production,
        consumption, give, but not trade(as its handled automatically).

        Args:
            'name'(string):
                the name of the current action/method the agent executes
            data_to_log:
                a dictianary with data for the database

        Example::

            self.log('profit', {'': profit})

            ... different method ...

            self.log('employment_and_rent', {'employment': self.possession('LAB'),
                                             'rent': self.possession('CAP'), 'composite': self.composite})

            for i in range(self.num_households):
                self.log('give%i' % i, self.give('Household', i, 'money', payout / self.num_households))

        See also:
            :meth:`~abecagent.Database.log_nested`:
                handles nested dictianaries
            :meth:`~abecagent.Database.log_change`:
                loges the change from last round
            :meth:`~abecagent.Database.observe_begin`:

        """
        data_to_write = {'%s_%s' % (action_name, key): data_to_log[key] for key in data_to_log}
        data_to_write['id'] = self.idn
        self.database_connection.send("log", zmq.SNDMORE)
        self.database_connection.send(self.group, zmq.SNDMORE)
        self.database_connection.send_json(data_to_write, zmq.SNDMORE)
        self.database_connection.send(str(self.round))

    def log_value(self, name, value):
        """ logs a value, with a name

        Args:
            'name'(string):
                the name of the value/variable
            value(int/float):
                the variable = value to log
        """
        self.database_connection.send("log", zmq.SNDMORE)
        self.database_connection.send(self.group, zmq.SNDMORE)
        self.database_connection.send_json({'id': self.idn, name: value}, zmq.SNDMORE)
        self.database_connection.send(str(self.round))

    def log_dict(self, action_name, data_to_log):
        """ same as the log function, only that it supports nested dictionaries
        see: :meth:`~abecagent.Database.log`.
        """
        data_to_write = flatten(data_to_log, '%s_' % action_name)
        data_to_write['id'] = self.idn
        self.database_connection.send("log", zmq.SNDMORE)
        self.database_connection.send(self.group, zmq.SNDMORE)
        self.database_connection.send_json(data_to_write, zmq.SNDMORE)
        self.database_connection.send(str(self.round))

    def log_change(self, action_name, data_to_log):
        """ This command logs the change in the variable from the round before.
        Important, use only once with the same action_name.

        Args:
            'name'(string):
                the name of the current action/method the agent executes
            data_to_log:
                a dictianary with data for the database

        Examples::

            self.log_change('profit', {'money': self.possession('money')]})
            self.log_change('inputs', {'money': self.possessions(['money', 'gold', 'CAP', 'LAB')]})
        """
        data_to_write = {}
        try:
            for key in data_to_log:
                data_to_write['%s_change_%s' % (action_name, key)] = data_to_log[key] - self._data_to_log_1[action_name][key]
        except KeyError:
            for key in data_to_log:
                data_to_write['%s_change_%s' % (action_name, key)] = data_to_log[key]
        data_to_write['id'] = self.idn
        self.database_connection.send("log", zmq.SNDMORE)
        self.database_connection.send(self.group, zmq.SNDMORE)
        self.database_connection.send_json(data_to_write, zmq.SNDMORE)
        self.database_connection.send(str(self.round))

        self._data_to_log_1[action_name] = data_to_log

    def observe_begin(self, action_name, data_to_observe):
        """ observe_begin and observe_end, observe the change of a variable.
        observe_begin(...), takes a list of variables to be observed.
        observe_end(...) writes the change in this vars into the log file

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

            self.log('employment_and_rent', {'employment': self.possession('LAB'),
                                            'rent': self.possession('CAP')})
        """
        self._data_to_observe[action_name] = data_to_observe

    def observe_end(self, action_name, data_to_observe):
        """ This command puts in a database called log, what ever values you
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

            self.log('employment_and_rent', {'employment': self.possession('LAB'),
                                            'rent':self.possession('CAP')})
        """
        before = self._data_to_observe.pop(action_name)
        data_to_write = {}
        for key in data_to_observe:
            data_to_write['%s_delta_%s' % (action_name, key)] = \
                                            data_to_observe[key] - before[key]
        data_to_write['id'] = self.idn
        self.database_connection.send("log", zmq.SNDMORE)
        self.database_connection.send(self.group, zmq.SNDMORE)
        self.database_connection.send_json(data_to_write, zmq.SNDMORE)
        self.database_connection.send(str(self.round))


def Offer(sender_group, sender_idn, receiver_group, receiver_idn, good, quantity, price, buysell='s', idn=None):
    offer = {}
    offer['sender_group'] = sender_group
    offer['sender_idn'] = sender_idn
    offer['receiver_group'] = receiver_group
    offer['receiver_idn'] = receiver_idn
    offer['good'] = good
    offer['quantity'] = quantity
    offer['price'] = price
    offer['buysell'] = buysell
    offer['idn'] = idn
    return offer


class Agent(Database, Trade, Messaging, multiprocessing.Process):
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
        self._msgs = {}

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

    def possessions_filter(self, goods=None, but=None, match=None, typ=None):
        """ returns a subset of the goods an agent owns, all arguments
        can be combined.

        Args:
            goods (list, optional):
                a list of goods to return
            but(list, optional):
                all goods but the list of goods here.
            match(string, optional TODO):
                goods that match pattern
            begin_with(string, optional TODO):
                all goods that begin with string
            end_with(string, optional TODO)
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
        if but:
            try:
                goods = set(goods) - set(but)
            except TypeError:
                raise SystemExit("goods and/or but must be a list e.G. ['element1', 'element2']")
        return dict((good, self._haves[good]) for good in goods)

    def _offer_counter(self):
        """ returns a unique number for an offer (containing the agent's name)
        """
        self._offer_count += 1
        return str(self.name) + str(self._offer_count)

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
        self.database_connection.send_json(self._trade_log, zmq.SNDMORE)
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
        try:
            self._haves[good] += quantity
        except KeyError:
            self._haves[good] = quantity

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
            addressee = self.commands.recv()
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
                if self.given_offers[key]['good'] == good:
                    self.given_offers[key]['status'] == 'perished'

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
        self.database_connection.send_json(data_to_track, zmq.SNDMORE)
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
                print('Warning:     %s has received offers that have not been polled with '
                'get_offers(...) or get_offers_all() in this round the '
                'offer_id is: "%s" and the good is "%s"' % (self.name, offer_id, good))
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
        self.aesof = self.commands.recv_json()

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
            msg = self.messages_in.recv_json()
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
            else:
                self._msgs.setdefault(typ, []).append(Message(msg))

        while True:
            address = self.shout.recv()
            if address == 'all.':
                break
            typ = self.shout.recv()
            msg = self.shout.recv_json()
            print msg
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
        self.out.send_json(msg)

    def _send_to_group(self, receiver_group, typ, msg):
        """ sends a message to 'receiver_group', who can be an agent, a group or
        'all'. The agents receives it at the begin of each round in
        self.messages(typ) is 'm' for mails.
        typ =(_o,c,u,r) are
        reserved for internally processed offers.
        """
        print '! ', receiver_group.encode('ascii'), typ, msg
        self.out.send('!', zmq.SNDMORE)
        self.out.send('s', zmq.SNDMORE)
        self.out.send('%s:' % receiver_group.encode('ascii'), zmq.SNDMORE)
        self.out.send(typ, zmq.SNDMORE)
        self.out.send_json(msg)


def flatten(d, parent_key=''):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s_' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)
