
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
#******************************************************************************************
# trade.pyx is written in cython. trade.pyx is not distributed for installation.
# instead, when you modify trade.pyx you need to compile it with compile.sh and compile.py
# and the resulting trade.c file, is distributed. Don't forget to commit it to git
#******************************************************************************************
from __future__ import division
from random import shuffle
from abce.tools import NotEnoughGoods
from messaging import Message
from libc.float cimport DBL_EPSILON
cdef extern from "numpy/npy_math.h":
    bint npy_isfinite(double x)


cdef double fmax(double a, double b):
    if a > b:
        return a
    else:
        return b


cdef class Offer:
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
        status:
            'new':
                has been created, but not answered
            'accepted':
                trade fully accepted
            'rejected':
                trade rejected
            'pending':
                offer has not yet answered, and is not older than one round.
            'perished':
                the **perishable** good was not accepted by the end of the round
                and therefore perished.
        final_quantity:
            If the offer has been answerd this returns the actual quantity
            bought or sold. (Equal to quantity if the offer was accepted fully)
        idn:
            a unique identifier
    """
    cdef readonly str sender_group
    cdef readonly int sender_idn
    cdef readonly str receiver_group
    cdef readonly int receiver_idn
    cdef readonly str good
    cdef readonly double quantity
    cdef readonly double price
    cdef readonly char buysell
    cdef public str status
    cdef public double final_quantity
    cdef readonly object idn
    cdef readonly int made
    cdef public str open_offer_status
    cdef public int status_round

    def __cinit__(self, str sender_group, int sender_idn, str receiver_group,
                  int receiver_idn, str good, double quantity, double price,
                  char buysell, str status, double final_quantity, long idn,
                  int made, str open_offer_status, int status_round):
        self.sender_group = sender_group
        self.sender_idn = sender_idn
        self.receiver_group = receiver_group
        self.receiver_idn = receiver_idn
        self.good = good
        self.quantity = quantity
        self.price = price
        self.buysell = buysell
        self.status = status
        self.final_quantity = final_quantity
        self.idn = idn
        self.made = made
        self.open_offer_status = open_offer_status
        self.status_round = status_round


    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def pickle(self):
        return (self.sender_group, self.sender_idn, self.receiver_group,
                self.receiver_idn, self.good, self.quantity, self.price,
                self.buysell, self.status, self.final_quantity, self.idn,
                self.made, self.open_offer_status, self.status_round)

    def __repr__(self):
        return """sender: %s, %i, receiver_group: %s,
                receiver_idn: %i, good: %s, quantity: %f, price: %f,
                buysell: %s, status: %s, final_quantity: % f, idn: %i,
                made: %i, open_offer_status: % s, status_round: %i """ % (

                    self.sender_group, self.sender_idn, self.receiver_group,
                    self.receiver_idn, self.good, self.quantity, self.price,
                    self.buysell, self.status, self.final_quantity, self.idn,
                    self.made, self.open_offer_status, self.status_round)

class Trade:
    """ Agents can trade with each other. The clearing of the trade is taken care
    of fully by ABCE.
    Selling a good works in the following way:

    1. An agent sends an offer. :meth:`~abceagent.Trade.sell`

       *The good offered is blocked and self.possession(...) does not account for it.*

    2. **Next subround:** An agent receives the offer :meth:`~abceagent.Trade.get_offers`, and can
       :meth:`~abceagent.Trade.accept`, :meth:`~abceagent.Trade.reject` or partially accept it. :meth:`~abceagent.Trade.accept`

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
                if offer.price < 0.3:
                    try:
                        self.accept(offer)
                    except NotEnoughGoods:
                        self.accept(offer, self.possession('money') / offer.price)
                else:
                    self.reject(offer)

        # Agent 1, subround 3
        def learning(self):
            offer = self.info(self.remember_trade)
            if offer.status == 'reject':
                self.price *= .9
            elif offer.status = 'accepted':
                self.price *= offer.final_quantity / offer.quantity
    """
    def get_offers_all(self, descending=False):
        """ returns all offers in a dictionary, with goods as key. The in each
        goods-category the goods are ordered by price. The order can be reversed
        by setting descending=True

        *Offers that are not accepted in the same subround (def block) are
        automatically rejected.* However you can also manually reject.

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
            print(offer.price, offer.sender)

        Lists can only efficiently pop the last item. Therefore it is more
        efficient to order backwards and buy the last good first::

         def buy_input_good(self):
            offers = self.get_offers_all(descending=True)
            while offers:
                if offers[good][-1]['quantity'] == self.prices_for_which_buy[good]:
                    self.accept(offers[good].pop())
        """
        return {good: self.get_offers(good, descending) for good in self._open_offers}

    def get_offers(self, good, descending=False):
        """ returns all offers of the 'good' ordered by price.

        *Offers that are not accepted in the same subround (def block) are
        automatically rejected.* However you can also manualy reject.

        peek_offers can be used to look at the offers without them being
        rejected automatically

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
                if offer.price < 50:
                    self.accept(offer)
                elif offer.price < 100:
                    self.accept(offer, 1)
                else:
                    self.reject(offer)  # optional
        """
        cdef Offer offer
        ret = []
        for offer in self._open_offers[good].values():
            offer.open_offer_status = 'polled'
            ret.append(offer)
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
                if offer.price < 50:
                    self.accept(offer)
                elif offer.price < 100:
                    self.accept(offer, 1)
                else:
                    self.reject(offer)  # optional
        """
        cdef Offer offer
        ret = []
        for offer in self._open_offers[good].values():
            offer.open_offer_status = 'peak_only'
            ret.append(offer)
        shuffle(ret)
        ret.sort(key=lambda objects: objects['price'], reverse=descending)
        return ret

    def sell(self, receiver_group, receiver_idn, good, double quantity, double price):
        """ commits to sell the quantity of good at price

        The good is not available for the agent. When the offer is
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
                if offer.status == 'accepted':
                    print(offer.final_quantity , 'cookies have be bougth')
                else:
                    offer.status == 'rejected':
                    print('On diet')
        """
        cdef double available
        price = bound_zero(price)
        # makes sure the quantity is between zero and maximum available, but
        # if its only a little bit above or below its set to the bounds
        available = self._haves[good]
        quantity = bound_zero(quantity)
        if quantity > available + DBL_EPSILON + DBL_EPSILON * fmax(quantity, available):
            raise NotEnoughGoods(self.name, good, quantity - available)
        if quantity > available:
            quantity = available

        offer_idn = self._offer_counter()
        self._haves[good] -= quantity
        cdef Offer offer = Offer(self.group,
                                 self.idn,
                                 receiver_group,
                                 receiver_idn,
                                 good,
                                 quantity,
                                 price,
                                 115,
                                 'new',
                                 -2,
                                 offer_idn,
                                 self.round,
                                 '-',
                                 -2)
        self.given_offers[offer_idn] = offer
        self._send(receiver_group, receiver_idn, '_o', offer.pickle())
        return offer

    def buy(self, receiver_group, receiver_idn, good, double quantity, double price):
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
        cdef double available
        cdef double money_amount
        price = bound_zero(price)
        money_amount = quantity * price
        # makes sure the money_amount is between zero and maximum available, but
        # if its only a little bit above or below its set to the bounds
        available = self._haves['money']
        money_amount = bound_zero(money_amount)
        if money_amount > available + DBL_EPSILON + DBL_EPSILON * fmax(money_amount, available):
            raise NotEnoughGoods(self.name, 'money', money_amount - available)
        if money_amount > available:
            money_amount = available

        offer_idn = self._offer_counter()
        self._haves['money'] -= money_amount
        cdef Offer offer = Offer(self.group,
                                 self.idn,
                                 receiver_group,
                                 receiver_idn,
                                 good,
                                 quantity,
                                 price,
                                 98,
                                 'new',
                                 -1,
                                 offer_idn,
                                 self.round,
                                 '',
                                 -1)
        self._send(receiver_group, receiver_idn, '_o', offer.pickle())
        self.given_offers[offer_idn] = offer
        return offer

    def retract(self, Offer offer):
        """ The agent who made a buy or sell offer can retract it

        The offer an agent made is deleted at the end of the sub-round and the
        committed good reappears in the haves. However if another agent
        accepts in the same round the trade will be cleared and not retracted.

        Args:
            offer: the offer he made with buy or sell
            (offer not quote!)
        """
        self._send(offer.receiver_group, '_d', offer)
        del self.given_offers[offer.idn]


    def accept(self, Offer offer, double quantity=-999):
        """ The buy or sell offer is accepted and cleared. If no quantity is
        given the offer is fully accepted; If a quantity is given the offer is
        partial accepted

        Args:

            offer:
                the offer the other party made
            quantity:
                quantity to accept. If not given all is accepted

        Return:
            Returns a dictionary with the good's quantity and the amount paid.
        """
        cdef double money_amount
        cdef double offer_quantity = offer.quantity
        cdef double available

        if quantity == -999:
            quantity = offer_quantity
        quantity = bound_zero(quantity)
        if quantity > offer_quantity + DBL_EPSILON * fmax(quantity, offer_quantity):
            raise AssertionError('accepted more than offered %s: %.100f >= %.100f'
                                 % (offer.good, quantity, offer_quantity))
        if quantity > offer_quantity:
            quantity = offer_quantity

        money_amount = quantity * offer.price
        if offer.buysell == 115:  # ord('s')
            money_amount = bound_zero(money_amount)
            available = self._haves['money']
            if money_amount > available + DBL_EPSILON + DBL_EPSILON * max(money_amount, available):
                raise NotEnoughGoods(self.name, 'money', money_amount - available)
            if money_amount > available:
                money_amount = available
            self._haves[offer.good] += quantity
            self._haves['money'] -= quantity * offer.price
        else:
            quantity = bound_zero(quantity)
            available = self._haves[offer.good]
            if quantity > available + DBL_EPSILON + DBL_EPSILON * max(quantity, available):
                raise NotEnoughGoods(self.name, offer.good, quantity - available)
            if quantity > available:
                quantity = available
            self._haves[offer.good] -= quantity
            self._haves['money'] += quantity * offer.price
        offer.final_quantity = quantity
        self._send(offer.sender_group, offer.sender_idn, '_p', (offer.idn, quantity))
        del self._open_offers[offer.good][offer.idn]
        return {offer.good: quantity, 'money': money_amount}

    def reject(self, Offer offer):
        """ The offer is rejected

        Args:
            offer: the offer the other party made
            (offer not quote!)
        """
        self._send(offer.sender_group, offer.sender_idn, '_r', offer.idn)
        del self._open_offers[offer.good][offer.idn]

    def _log_receive_accept_group(self, Offer offer):
        if offer.buysell == 115:
            self._trade_log['%s,%s,%s,%f' % (offer.good, self.group, offer.receiver_group, offer.price)] += offer.quantity
        else:
            self._trade_log['%s,%s,%s,%f' % (offer.good, offer.receiver_group, self.group, offer.price)] += offer.quantity

    def _log_receive_accept_agent(self, Offer offer):
        if offer.buysell == 115:
            self._trade_log['%s,%s,%s,%f' % (offer.good, self.name_without_colon, '%s_%i' % (offer.receiver_group, offer.receiver_idn), offer.price)] += offer.quantity
        else:
            self._trade_log['%s,%s,%s,%f' % (offer.good, '%s_%i' % (offer.receiver_group, offer.receiver_idn), self.name_without_colon, offer.price)] += offer.quantity

    def _receive_accept(self, offer_idn_final_quantity):
        """ When the other party partially accepted the  money or good is
        received, remaining good or money is added back to haves and the offer
        is deleted
        """
        cdef Offer offer = self.given_offers[offer_idn_final_quantity[0]]
        offer.final_quantity = offer_idn_final_quantity[1]
        if offer.buysell == 115:
            self._haves['money'] += offer.final_quantity * offer.price
            self._haves[offer.good] += offer.quantity - offer.final_quantity
        else:
            self._haves[offer.good] += offer.final_quantity
            self._haves['money'] += (offer.quantity - offer.final_quantity) * offer.price
        offer.status = "accepted"
        offer.status_round = self.round
        del self.given_offers[offer.idn]
        return offer

    def _log_receive_accept_group(self, Offer offer):
        if offer.buysell == 115:
            self._trade_log['%s,%s,%s,%f' % (offer.good, self.group, offer.receiver_group, offer.price)] += offer.final_quantity
        else:
            self._trade_log['%s,%s,%s,%f' % (offer.good, offer.receiver_group, self.group, offer.price)] += offer.final_quantity

    def _log_receive_accept_agent(self, Offer offer):
        if offer.buysell == 115:
            self._trade_log['%s,%s,%s,%f' % (offer.good, self.name_without_colon, '%s_%i' % (offer.receiver_group, offer.receiver_idn), offer.price)] += offer.final_quantity
        else:
            self._trade_log['%s,%s,%s,%f' % (offer.good, '%s_%i' % (offer.receiver_group, offer.receiver_idn), self.name_without_colon, offer.price)] += offer.final_quantity

    def _receive_reject(self, offer_id):
        """ delets a given offer

        is used by _msg_clearing__end_of_subround, when the other party rejects
        or at the end of the subround when agent retracted the offer

        """
        cdef Offer offer = self.given_offers[offer_id]
        if offer.buysell == 115:
            self._haves[offer.good] += offer.quantity
        else:
            self._haves['money'] += offer.quantity * offer.price
        offer.status = "rejected"
        offer.status_round = self.round
        del self.given_offers[offer_id]

    def _delete_given_offer(self, offer_id):
        cdef Offer offer = self.given_offers.pop(offer_id)
        if offer.buysell == 115:
            self._haves[offer.good] += offer.quantity
        else:
            self._haves['money'] += offer.quantity * offer.price

    def give(self, receiver_group, receiver_idn, good, double quantity):
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
        cdef double available
        quantity = bound_zero(quantity)
        available = self._haves[good]
        if quantity > available + DBL_EPSILON + DBL_EPSILON * max(quantity, available):
            raise NotEnoughGoods(self.name, good, quantity - available)
        if quantity > available:
            quantity = available
        self._haves[good] -= quantity
        self._send(receiver_group, receiver_idn, '_g', [good, quantity])
        return {good: quantity}

    def take(self, receiver_group, receiver_idn, good, quantity):
        """ take a good from another agent. The other agent has to accept.
        Args:

            receiver_group, receiver_idn, good, quantity
        """
        self.buy(receiver_group, receiver_idn, good=good, quantity=quantity, price=0)


    def _clearing__end_of_subround(self, incomming_messages):
        """ agent receives all messages and objects that have been send in this
        subround and deletes the offers that where retracted, but not executed.

        '_o': registers a new offer
        '_d': delete received that the issuing agent retract
        '_p': clears a made offer that was accepted by the other agent
        '_r': deletes an offer that the other agent rejected
        '_g': recive a 'free' good from another party
        """
        cdef Offer offer
        for typ, msg in incomming_messages:
            if typ == '_o':
                offer = Offer(*msg)
                offer.open_offer_status ='received'
                self._open_offers[offer.good][offer.idn] = offer
            elif typ == '_d':
                del self._open_offers[msg.good][msg.idn]
            elif typ == '_p':
                offer = self._receive_accept(msg)
                if self.trade_logging == 2:
                    self._log_receive_accept_group(offer)
                elif self.trade_logging == 1:
                    self._log_receive_accept_agent(offer)
            elif typ == '_r':
                self._receive_reject(msg)
            elif typ == '_g':
                self._haves[msg[0]] += msg[1]
            elif typ == '_q':
                self._quotes[msg.idn] = msg
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
                self._haves[msg.good] += msg.quantity
                self._contracts_delivered.append((msg.receiver_group, msg.receiver_idn))
                self._log_receive_accept(msg)
            elif typ == '!p':
                self._haves['money'] += msg.price
                self._contracts_payed.append((msg.receiver_group, msg.receiver_idn))
                self._log_receive_accept(msg)
            else:
                self._msgs.setdefault(typ, []).append(Message(msg))

cdef double bound_zero(double x):
    """ asserts that variable is above zero, where foating point imprecission is accounted for,
    and than makes sure it is above 0, without floating point imprecission """
    assert x > - DBL_EPSILON, '%.30f is smaller than 0 - epsilon (%.30f)' % (x, - DBL_EPSILON)
    assert npy_isfinite(x), x
    if x < 0:
        return 0
    else:
        return x
