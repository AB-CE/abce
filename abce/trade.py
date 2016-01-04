
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
from abce.tools import is_zero, NotEnoughGoods, is_negative, is_positive, epsilon, bound_zero, a_smaller_b
from sys import float_info
save_err = np.seterr(invalid='ignore')


def Offer(sender_group, sender_idn, receiver_group, receiver_idn, good, quantity, price, buysell, idn):
    """ This is an offer container that is send to the other agent. You can
    access the offer container both at the receiver as well as at the sender,
    if you have saved the offer. (e.G. self.offer = self.sell(...)). You should
    NEVER CHANGE the offer container.

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
    pass

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
                if offer['price'] < 0.3:
                    try:
                        self.accept(offer)
                    except NotEnoughGoods:
                        self.accept(offer, self.possession('money') / offer['price'])
                else:
                    self.reject(offer)

        # Agent 1, subround 3
        def learning(self):
            if self.offer['status'] == 'reject':
                self.price *= .9
            elif self.offer['status'] = 'accepted':
                self.price *= self.offer['final_quantity'] / self.offer['quantity']
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
            print(offer['price'], offer['sender'])

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
                if offer['price'] < 50:
                    self.accept(offer)
                elif offer['price'] < 100:
                    self.accept(offer, 1)
                else:
                    self.reject(offer)  # optional
        """
        ret = []
        for offer in self._open_offers[good].values():
            offer['open_offer_status'] = 'polled'
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
                if offer['price'] < 50:
                    self.accept(offer)
                elif offer['price'] < 100:
                    self.accept(offer, 1)
                else:
                    self.reject(offer)  # optional
        """
        ret = []
        for offer in self._open_offers[good].values():
            offer['open_offer_status'] = 'peak_only'
            ret.append(offer)
        shuffle(ret)
        ret.sort(key=lambda objects: objects['price'], reverse=descending)
        return ret

    def sell(self, receiver_group, receiver_idn, good, quantity, price):
        """ commits to sell the quantity of good at price

        The good is not available for the agent. When the offer is
        rejected it is automatically re-credited. When the offer is
        accepted the money amount is credited. (partial acceptance
        accordingly)

        Args:
            receiver_group:
                an agent name  NEVER a group or 'all'!!!
            (its an error but with a confusing warning)
            'good':
                name of the good
            quantity:
                maximum units disposed to buy at this price
            price:
                price per unit

        Returns:
            An Offer object. The offer object is a dictionary, that gives
            information about a trade. An offer object should not be
            manipulated.

        Example::

            Agent_1:
                def subround_1(self):
                    self.offer = self.sell('household', 1, 'cookies', quantity=5, price=0.1)

                def subround_3(self):
                    if self.offer['status'] == 'accepted':
                        print(self.offer['final_quantity'] , 'cookies have be bought')
                    else:
                        self.offer['status'] == 'rejected':
                        print('On diet')

            Agent_2:
                def subround_2(self):
                    offers = self.get_offers('cookies')
                    for offer in offers:
                        if offer['price'] < 1:
                            self.accept(offer)
                        if offer['price'] < 2:
                            self.accept(offer, offer['quantity'] / 2)
                        else:
                            self.reject(offer)
        """
        price = bound_zero(price)
        quantity = self._quantity_smaller_goods(quantity, good)
        self._haves[good] -= quantity
        offer = {'sender_group': self.group,
                 'sender_idn': self.idn,
                 'receiver_group': receiver_group,
                 'receiver_idn': receiver_idn,
                 'good': good,
                 'quantity': quantity,
                 'price': price,
                 'buysell': 's',
                 'status': 'new',
                 'made': self.round,
                 'idn': self._offer_counter()}
        self._send(receiver_group, receiver_idn, '_o', offer)
        self.given_offers[offer['idn']] = offer
        return offer

    def buy(self, receiver_group, receiver_idn, good, quantity, price):
        """ commits to sell the quantity of good at price

        The goods are not in haves or self.count(). When the offer is
        rejected it is automatically re-credited. When the offer is
        accepted the money amount is credited. (partial acceptance
        accordingly)

        Args:
            receiver_group:
                an agent name  NEVER a group or 'all'!
            (it is an error but with a confusing warning)
            'good':
                name of the good
            quantity:
                maximum units disposed to buy at this price
            price:
                price per unit

        Returns:
            An offer object. The offer object is a dictionary, that gives
            information about a trade. An offer object should not be
            manipulated.


        Example::

            Agent_1:
                def subround_1(self):
                    self.offer = self.buy('firm', 1, 'cookies', quantity=5, price=0.1)

                def subround_3(self):
                    if self.offer['status'] == 'accepted':
                        print(self.offer['final_quantity'] , 'cookies have been sold to me')
                    else:
                        self.offer['status'] == 'rejected':
                        print('Want cookies')

            Agent_2:
                def subround_2(self):
                    offers = self.get_offers('cookies')
                    for offer in offers:
                        if offer['price'] > 2:
                            self.accept(offer)
                        if offer['price'] > 1:
                            self.accept(offer, offer['quantity'] / 2)
                        else:
                            self.reject(offer)
        """
        price = bound_zero(price)
        money_amount = quantity * price
        money_amount = self._quantity_smaller_goods(money_amount, 'money')
        self._haves['money'] -= money_amount
        offer = {'sender_group': self.group,
                 'sender_idn': self.idn,
                 'receiver_group': receiver_group,
                 'receiver_idn': receiver_idn,
                 'good': good,
                 'quantity': quantity,
                 'price': price,
                 'buysell': 'b',
                 'status': 'new',
                 'made': self.round,
                 'idn': self._offer_counter()}
        self._send(receiver_group, receiver_idn, '_o', offer)
        self.given_offers[offer['idn']] = offer
        return offer

    def retract(self, offer):
        """ The agent who made a buy or sell offer can retract it

        The offer an agent made is deleted at the end of the sub-round and the
        committed good reappears in the haves. However if another agent
        accepts in the same round the trade will be cleared and not retracted.

        Args:
            offer: the offer he made with buy or sell
            (offer not quote!)
        """
        self._send(offer['receiver_group'], '_d', offer)
        del self.given_offers[offer['idn']]


    def accept(self, offer, quantity=None):
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
        if quantity is None:
            quantity = offer['quantity']
        quantity = bound_zero(quantity)
        try:
            quantity = a_smaller_b(quantity, offer['quantity'])
        except AssertionError:
            raise AssertionError('accepted more than offered %s: %.100f >= %.100f'
                                 % (offer['good'], quantity, offer['quantity']))
        money_amount = quantity * offer['price']
        if offer['buysell'] == 's':
            money_amount = self._quantity_smaller_goods(money_amount, 'money')
            self._haves[offer['good']] += quantity
            self._haves['money'] -= quantity * offer['price']
        else:
            quantity = self._quantity_smaller_goods(quantity, offer['good'])
            self._haves[offer['good']] -= quantity
            self._haves['money'] += quantity * offer['price']
        offer['final_quantity'] = quantity
        self._send(offer['sender_group'], offer['sender_idn'], '_p', offer)
        del self._open_offers[offer['good']][offer['idn']]
        return {offer['good']: quantity, 'money': money_amount}

    def reject(self, offer):
        """ The offer is rejected

        Args:
            offer: the offer the other party made
            (offer not quote!)
        """
        self._send(offer['sender_group'], offer['sender_idn'], '_r', offer['idn'])
        del self._open_offers[offer['good']][offer['idn']]

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

    def _receive_accept(self, offer):
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
        offer['status'] = "accepted"
        offer['status_round'] = self.round
        del self.given_offers[offer['idn']]
        return offer

    def _log_receive_accept_group(self, offer):
        if offer['buysell'] == 's':
            self._trade_log['%s,%s,%s,%f' % (offer['good'], self.group, offer['receiver_group'], offer['price'])] += offer['final_quantity']
        else:
            self._trade_log['%s,%s,%s,%f' % (offer['good'], offer['receiver_group'], self.group, offer['price'])] += offer['final_quantity']

    def _log_receive_accept_agent(self, offer):
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
        del self.given_offers[offer_id]

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
        quantity = bound_zero(quantity)
        quantity = self._quantity_smaller_goods(quantity, good)
        self._haves[good] -= quantity
        self._send(receiver_group, receiver_idn, '_g', [good, quantity])
        return {good: quantity}

    def take(self, receiver_group, receiver_idn, good, quantity):
        """ take a good from another agent. The other agent has to accept.
        Args:

            receiver_group, receiver_idn, good, quantity
        """
        self.buy(receiver_group, receiver_idn, good=good, quantity=quantity, price=0)

    def _quantity_smaller_goods(self, quantity, good):
        """ asserts that quantity is smaller then goods, taking floating point imprecission into account and
        then sets a so that it is exacly smaller or equal the available """
        available = self._haves[good]
        if quantity > available + float_info.epsilon + float_info.epsilon * max(abs(quantity), abs(available)):
            raise NotEnoughGoods(self.name, good, quantity - available)
        quantity = bound_zero(quantity)
        if quantity <= available:
            return quantity
        else:
            return available

