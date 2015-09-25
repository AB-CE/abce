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
from collections import defaultdict
import numpy as np
from random import shuffle
from abce.tools import is_zero, is_positive, is_negative, NotEnoughGoods, epsilon
save_err = np.seterr(invalid='ignore')


def Offer(sender_group, sender_idn, receiver_group, receiver_idn, good, quantity, price, buysell, idn):
    """ This is an offer container that is send to the other agent. You can
    access the offer container both at the receiver as well as at the sender,
    if you have saved the offer. (e.G. self.offer = self.sell(...))

    Args:
        sender_group:
            this is the group name of the sender
        sender_idn:
            this is the ID of the sender
        receiver_group:
            This is the group name of the receiver
        receiver_idn:
            this is the ID of the sender
        good:
            the good offered or demanded
        quantity:
            the quantity offered or demanded
        price:
            the suggested tansaction price
        buysell:
            this can have the values 'b' for buy; 's' for sell; 'qb' for a
            nonbinding buy quote; and 'qs' for a nonbinding sell quote

        idn:
            a unique identifier
    """
    pass


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

       - in case of acceptance *the money is automatically credited.*
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
    :meth:`~abceagent.Trade.accept_quote_partial`, send a committed offer that it is the uncommitted price quote.


    """
    def get_quotes(self, good, descending=False):
        """ self.get_quotes() returns all new quotes and removes them. The order
        is randomized.

        Args:
            good:
                the good which should be retrieved
            descending(bool,default=False):
                False for descending True for ascending by price

        Returns:
         list of quotes ordered by price

        Example::

         quotes = self.get_quotes()
        """
        ret = []
        for offer_idn in self._quotes.keys():
            if self._quotes[offer_idn]['good'] == good:
                ret.append(self._quotes[offer_idn])
                del self._quotes[offer_idn]
        ret.sort(key=lambda objects: objects['price'], reverse=descending)
        return ret

    def get_quotes_all(self, descending=False):
        """ self.get_quotes_all() returns a dictionary with all now new quotes ordered
        by the good type and removes them. The order is randomized.

        Args:
            descending(bool,default=False):
                False for descending True for ascending by price

        Returns:
            dictionary of list of quotes ordered by price. The dictionary
            itself is ordered by price.

        Example::

            quotes = self.get_quotes()
        """
        ret = defaultdict(list)

        for quote in self._quotes:
            key = self._quotes[quote]['good']
            ret[key].append(self._quotes[quote])
        for key in ret.keys():
            shuffle(ret[key])
            ret[key].sort(key=lambda objects: objects['price'], reverse=descending)
        self._quotes = {}
        return ret

    def info(self, offer_idn):
        """ lets you access all fields of a **given** offer.
        This allows you to check whether an offer was accepted, partially accepted
        or rejected and retrieve the quantity actually traded.

        If in your first round the value you are testing is not set, set the variable
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
                'pending':
                    offer has not yet answered, and is not older than one round.
                'perished':
                    the **perishable** good was not accepted by the end of the round
                    and therefore perished.
            ['quantity']:
                the quantity of the original quote.
            ['final_quantity']:
                This returns the actual quantity bought or sold. (Equal to quantity
                    if the offer was accepted fully)

        Raises:
            KeyError:
                If the offer was answered more than one round ago.

        Example Pending::

            status = self.info(self.offer_idn)['status']
            if status == 'pending':
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
                reinforcement_learner.integrateObservation([self.info(self.offer)])
                reinforcement_learner.giveReward([self.info(self.offer) * price - self.car_cost])
        """
        offer = self.given_offers[offer_idn]
        try:
            if offer['status'] == 'accepted':
                offer['final_quantity'] = offer['quantity']
            elif  offer['status'] == 'rejected':
                offer['final_quantity'] = 0
        except KeyError:
            offer['status'] = 'pending'
        return offer

    def partial_status_percentage(self, offer_idn):
        """ returns the percentage of a partial accept

        Args:
            offer_idn:
                on offer as returned by self.sell(...) ord self.buy(...)

        Returns:
            A value between [0, 1]

        Raises:
            KeyError, when no answer has been given or received more than one round before
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
            self.buy(quote['sender_group'], quote['sender_idn'], quote['good'], quote['quantity'], quote['price'])
        else:
            self.sell(quote['sender_group'], quote['sender_idn'], quote['good'], quote['quantity'], quote['price'])

    def accept_quote_partial(self, quote, quantity):
        """ makes a commited buy or sell out of the counterparties quote

        Args::
         quote: buy or sell quote that is accepted
         quantity: the quantity that is offered/requested
         it should be less than propsed in the quote, but this is not enforced.

        """
        if quote['buysell'] == 'qs':
            self.buy(quote['sender_group'], quote['sender_idn'], quote['good'], quantity, quote['price'])
        else:
            self.sell(quote['sender_group'], quote['sender_idn'], quote['good'], quantity, quote['price'])

    #TODO create assert unanswered offers

    def get_offers_all(self, descending=False):
        """ returns all offers in a dictionary, with goods as key. The in each
        goods-category the goods are ordered by price. The order can be reversed
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
        efficient to order backwards and buy the last good first::

         def buy_input_good(self):
            offers = self.get_offers_all(descending=True)
            while offers:
                if offers[good][-1]['quantity'] == self.prices_for_which_buy[good]:
                    self.accept(offers[good].pop())
        """
        offers_by_good = defaultdict(list)
        for offer_id in self._open_offers:
            self._open_offers[offer_id]['open_offer_status'] = 'polled'
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

        Args:
            good:
                the good which should be retrieved
            descending(bool,default=False):
                False for descending True for ascending by price

        Returns:
            A list of offers ordered by price

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
                self._open_offers[offer_idn]['open_offer_status'] = 'polled'
                ret.append(self._open_offers[offer_idn])
        shuffle(ret)
        ret.sort(key=lambda objects: objects['price'], reverse=descending)
        return ret

    def peak_offers(self, good, descending=False):
        """ returns a peak on all offers of the 'good' ordered by price.
        Peaked offers can not be accepted or rejected, but they do not
        expire.

        Args:
            good:
                the good which should be retrieved
                descending(bool,default=False):
                False for descending True for ascending by price

        Returns:
            A list of offers ordered by price

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
                offer = self._open_offers[offer_idn]
                offer['open_offer_status'] = 'peak_only'
                ret.append(offer)
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
        offer = {'sender_group': self.group,
                 'sender_idn': self.idn,
                 'receiver_group': receiver_group,
                 'receiver_idn': receiver_idn,
                 'good': good,
                 'quantity': quantity,
                 'price': price,
                 'buysell': 'qs',
                 'idn': self._offer_counter()}
        self._send(receiver_group, receiver_idn, '_q', offer)
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
        offer = {'sender_group': self.group,
                 'sender_idn': self.idn,
                 'receiver_group': receiver_group,
                 'receiver_idn': receiver_idn,
                 'good': good,
                 'quantity': quantity,
                 'price': price,
                 'buysell': 'qb',
                 'idn': self._offer_counter()}
        self._send(receiver_group, receiver_idn, '_q', offer)
        return offer

    def sell(self, receiver_group, receiver_idn, good, quantity, price):
        """ commits to sell the quantity of good at price

        The goods are not in haves or self.count(). When the offer is
        rejected it is automatically re-credited. When the offer is
        accepted the money amount is credited. (partial acceptance
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
        if self._haves[good] < quantity - epsilon:
            raise NotEnoughGoods(self.name, good, quantity - self._haves[good])
        self._haves[good] -= quantity
        offer = {'sender_group': self.group,
                 'sender_idn': self.idn,
                 'receiver_group': receiver_group,
                 'receiver_idn': receiver_idn,
                 'good': good,
                 'quantity': quantity,
                 'price': price,
                 'buysell': 's',
                 'idn': self._offer_counter()}
        assert quantity >= - epsilon, quantity
        self._send(receiver_group, receiver_idn, '_o', offer)
        self.given_offers[offer['idn']] = offer
        return offer['idn']

    def sell_max_possible(self, receiver_group, receiver_idn, good, quantity, price):
        """ Same as sell but if the possession of good is smaller than the number,
        it executes the deal with a lower amount of goods using everything
        available of this good.
        """
        try:
            self.sell(receiver_group, receiver_idn, good, quantity, price)
        except NotEnoughGoods:
            self.sell(receiver_group, receiver_idn, good, quantity=self.possession(good), price=price)

    def buy(self, receiver_group, receiver_idn, good, quantity, price):
        """ commits to sell the quantity of good at price

        The goods are not in haves or self.count(). When the offer is
        rejected it is automatically re-credited. When the offer is
        accepted the money amount is credited. (partial acceptance
        accordingly)

        Args:
            receiver_group: an agent name  NEVER a group or 'all'!
            (it is an error but with a confusing warning)
            'good': name of the good
            quantity: maximum units disposed to buy at this price
            price: price per unit
        """
        money_amount = quantity * price
        if self._haves['money'] < money_amount - epsilon:
            raise NotEnoughGoods(self.name, 'money', money_amount - self._haves['money'])

        self._haves['money'] -= money_amount
        offer = {'sender_group': self.group,
                 'sender_idn': self.idn,
                 'receiver_group': receiver_group,
                 'receiver_idn': receiver_idn,
                 'good': good,
                 'quantity': quantity,
                 'price': price,
                 'buysell': 'b',
                 'idn': self._offer_counter()}
        assert quantity >= - epsilon, quantity
        self._send(receiver_group, receiver_idn, '_o', offer)
        self.given_offers[offer['idn']] = offer
        return offer['idn']

    def buy_max_possible(self, receiver_group, receiver_idn, good, quantity, price):
        """ Same as buy but if money is insufficient, it executes the deal with
        a lower amount of goods using all available money.
        """
        try:
            self.buy(receiver_group, receiver_idn, good, quantity, price)
        except NotEnoughGoods:
            self.buy(receiver_group, receiver_idn, good, quantity=self.possession('money') / price, price=price)


    def retract(self, offer_idn):
        """ The agent who made a buy or sell offer can retract it

        The offer an agent made is deleted at the end of the sub-round and the
        committed good reappears in the haves. However if another agent
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
        assert not(is_positive(quantity - offer['quantity'])), 'accepted more than offered %s: %f > %s' % (offer['good'], quantity, offer['quantity'])
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

    def accept_max_possible(self, offer):
        """ TODO The offer is partly accepted and cleared

        Args:
            offer: the offer the other party made
            (offer not quote!)

        Return:
            Returns a dictionary with the good's quantity and the amount paid.
        """
        try:
            self.accept(offer)
        except NotEnoughGoods:
            if offer['buysell'] == 's':
                self.accept_partial(offer, self.possession('money') / offer['price'])
            else:
                self.accept_partial(offer, self.possession(offer['good']))

    def accept_partial_max_possible(self, offer, quantity):
        """ TODO The offer is partly accepted and cleared

        Args:
            offer: the offer the other party made
            (offer not quote!)

        Return:
            Returns a dictionary with the good's quantity and the amount paid.
        """
        try:
            self.accept_partial(offer, quantity)
        except NotEnoughGoods:
            if offer['buysell'] == 's':
                self.accept_partial(offer, self.possession('money') / offer['price'])
            else:
                self.accept_partial(offer, self.possession(offer['good']))


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
            self._trade_log['%s,%s,%s,%f' % (offer['good'], self.name_without_colon, '%s_%i' % (offer['receiver_group'], offer['receiver_idn']), offer['price'])] += offer['quantity']
        else:
            self._trade_log['%s,%s,%s,%f' % (offer['good'], '%s_%i' % (offer['receiver_group'], offer['receiver_idn']), self.name_without_colon, offer['price'])] += offer['quantity']

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
            self._trade_log['%s,%s,%s,%f' % (offer['good'], self.name_without_colon, '%s_%i' % (offer['receiver_group'], offer['receiver_idn']), offer['price'])] += offer['final_quantity']
        else:
            self._trade_log['%s,%s,%s,%f' % (offer['good'], '%s_%i' % (offer['receiver_group'], offer['receiver_idn']), self.name_without_colon, offer['price'])] += offer['final_quantity']

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
            Dictionary, with the transfer, which can be used by self.log(...).

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
