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
The :class:`abceagent.Agent` class is the basic class for creating your agent. It
automatically handles the possession of goods of an agent. In order to produce/transform
goods you need to also subclass the :class:`abceagent.Firm` [1]_ or to create a consumer
the :class:`abceagent.Household`.

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
# ***************************************************************************************** #
#  trade.pyx is written in cython. When you modify trade.pyx you need to compile it with    #
# compile.sh and compile.py because the resulting trade.c file is distributed.              #
# Don't forget to commit it to git                                                          #
# ***************************************************************************************** #
import random
from collections import defaultdict, OrderedDict
from abce.notenoughgoods import NotEnoughGoods

epsilon = 0.00000000001


def get_epsilon():
    return epsilon


class Offer(object):
    __slots__ = ('sender', 'receiver', 'good', 'quantity', 'price', 'currency',
                 'sell', 'status', 'final_quantity', 'id',
                 'made', 'status_round')
    """ This is an offer container that is send to the other agent. You can
    access the offer container both at the receiver as well as at the sender,
    if you have saved the offer. (e.G. self.offer = self.sell(...))

    it has the following properties:
        sender_group:
            this is the group name of the sender

        sender:
            this is the  the sender

        receiver:
            this is the the sender

        currency:
            The other good against which the good is traded.

        good:
            the good offered or demanded

        quantity:
            the quantity offered or demanded

        price:
            the suggested transaction price

        sell:
            this can have the values False for buy; True for sell

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
        id:
            a unique identifier
    """
    def __init__(self, sender, receiver, good, quantity, price, currency,
                 sell, id, made):
        self.sender = sender
        self.receiver = receiver
        self.good = good
        self.currency = currency
        self.quantity = quantity
        self.price = price
        self.sell = sell
        self.status = 'new'
        self.final_quantity = None
        self.id = id
        self.made = made
        self.status_round = None

    def __repr__(self):
        return ("""<{sender: (%s, %i), receiver: (%s, %i), good: %s, quantity: %f, price: %f, currency: %f,
                sell: %s, status: %s, final_quantity: % f, id: %i, made: %i, status_round: %i }>""" %
                (*self.sender, *self.receiver, self.good, self.quantity, self.price, self.currency,
                 self.sell, self.status, self.final_quantity, self.id, self.made, self.status_round))


class Trade:
    """ Agents can trade with each other. The clearing of the trade is taken care
    of fully by ABCE.
    Selling a good works in the following way:

    1. An agent sends an offer. :meth:`~.sell`

       *ABCE does not allow you to sell the same good twice; self.free(good) shows how much good is not reserved yet*

    2. **Next subround:** An agent receives the offer :meth:`~.get_offers`, and can
       :meth:`~.accept`, :meth:`~.reject` or partially accept it. :meth:`~.accept`

       *The good is credited and the price is deducted from the agent's possessions.*

    3. **Next subround:**

       - in case of acceptance *the money is automatically credited.*
       - in case of partial acceptance *the money is credited and part of the reserved good is unblocked.*
       - in case of rejection *the good is unblocked.*

    Analogously for buying: :meth:`~.buy`

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
                        self.accept(offer, self['money'] / offer.price)
                else:
                    self.reject(offer)

        # Agent 1, subround 3
        def learning(self):
            offer = self.info(self.remember_trade)
            if offer.status == 'reject':
                self.price *= .9
            elif offer.status = 'accepted':
                self.price *= offer.final_quantity / offer.quantity
    Example::

        # Agent 1
        def sales(self):
            self.remember_trade = self.sell('Household', 0, 'cookies', quantity=5, price=self.price, currency='dollars')

        # Agent 2
        def receive_sale(self):
            oo = self.get_offers('cookies')
            for offer in oo:
                if ((offer.currency == 'dollars' and offer.price < 0.3 * exchange_rate)
                    or (offer.currency == 'euros' and dollars'offer.price < 0.3)):

                    try:
                        self.accept(offer)
                    except NotEnoughGoods:
                        self.accept(offer, self['money'] / offer.price)
                else:
                    self.reject(offer)

    If we did not implement a barter class, but one can use this class as a barter class,
    """
    def __init__(self, id, agent_parameters, simulation_parameters, group, trade_logging,
                 database, check_unchecked_msgs, expiring, perishable, resource_endowment, start_round=None):
        super(Trade, self).__init__(id, agent_parameters, simulation_parameters, group, trade_logging,
                                    database, check_unchecked_msgs, expiring, perishable, resource_endowment, start_round)
        self.given_offers = OrderedDict()
        self._open_offers_buy = defaultdict(dict)
        self._open_offers_sell = defaultdict(dict)
        self._polled_offers = {}
        self._offer_count = 0
        self.trade_logging = {'individual': 1,
                              'group': 2, 'off': 0}[trade_logging]
        self._trade_log = defaultdict(int)
        self._quotes = {}

    def _offer_counter(self):
        """ returns a unique number for an offer (containing the agent's name)
        """
        self._offer_count += 1
        return hash((self.name, self._offer_count))

    def _advance_round(self, time):
        if self.trade_logging > 0:
            self.database_connection.put(["trade_log", self._trade_log, self.round])
        self._trade_log = defaultdict(int)

    def get_buy_offers_all(self, descending=False, sorted=True):
        """ """
        goods = list(self._open_offers_buy.keys())
        return {good: self.get_buy_offers(good, descending, sorted) for good in goods}

    def get_sell_offers_all(self, descending=False, sorted=True):
        """ """
        goods = list(self._open_offers_sell.keys())
        return {good: self.get_sell_offers(good, descending, sorted) for good in goods}

    def get_offers_all(self, descending=False, sorted=True):
        """ returns all offers in a dictionary, with goods as key. The in each
        goods-category the goods are ordered by price. The order can be reversed
        by setting descending=True

        *Offers that are not accepted in the same subround (def block) are
        automatically rejected.* However you can also manually reject.

        Args:

         descending(optional):
            is a bool. False for descending True for ascending by price

         sorted(default=True):
                Whether offers are sorted by price. Faster if False.

        Returns:

            a dictionary with good types as keys and list of :class:`abce.trade.Offer`
            as values

        Example::

         oo = get_offers_all(descending=False)
         for good_category in oo:
            print('The cheapest good of category' + good_category
            + ' is ' + good_category[0])
            for offer in oo[good_category]:
                if offer.price < 0.5:
                    self.accept(offer)

         for offer in oo.beer:
            print(offer.price, offer.sender)
        """
        goods = list(self._open_offers_sell.keys() + self._open_offers_buy.keys())
        return {good: self.get_offers(good, descending, sorted) for good in goods}

    def get_buy_offers(self, good, sorted=True, descending=False, shuffled=True):
        """ """
        ret = list(self._open_offers_buy[good].values())
        self._polled_offers.update(self._open_offers_buy[good])
        del self._open_offers_buy[good]
        if shuffled:
            random.shuffle(ret)
        if sorted:
            ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def get_sell_offers(self, good, sorted=True, descending=False, shuffled=True):
        """ """
        ret = list(self._open_offers_sell[good].values())
        self._polled_offers.update(self._open_offers_sell[good])
        del self._open_offers_sell[good]
        if shuffled:
            random.shuffle(ret)
        if sorted:
            ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def get_offers(self, good, sorted=True, descending=False, shuffled=True):
        """ returns all offers of the 'good' ordered by price.

        *Offers that are not accepted in the same subround (def block) are
        automatically rejected.* However you can also manually reject.

        peek_offers can be used to look at the offers without them being
        rejected automatically

        Args:
            good:
                the good which should be retrieved

            sorted(bool, default=True):
                Whether offers are sorted by price. Faster if False.

            descending(bool, default=False):
                False for descending True for ascending by price

            shuffled(bool, default=True):
                whether the order of messages is randomized or correlated with
                the ID of the agent. Setting this to False speeds up the
                simulation considerably, but introduces a bias.

        Returns:
            A list of :class:`abce.trade.Offer` ordered by price.

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
        ret = (self.get_buy_offers(good, descending=False, sorted=False, shuffled=False) +
               self.get_sell_offers(good, descending=False, sorted=False, shuffled=False))
        if shuffled:
            random.shuffle(ret)
        if sorted:
            ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def peak_buy_offers(self, good, sorted=True, descending=False, shuffled=True):
        """ """
        ret = []
        for offer in self._open_offers_buy[good].values():
            ret.append(offer)
        if shuffled:
            random.shuffle(ret)
        if sorted:
            ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def peak_sell_offers(self, good, sorted=True, descending=False, shuffled=True):
        """ """
        ret = []
        for offer in self._open_offers_sell[good].values():
            ret.append(offer)
        if shuffled:
            random.shuffle(ret)
        if sorted:
            ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def peak_offers(self, good, sorted=True, descending=False, shuffled=True):
        """ returns a peak on all offers of the 'good' ordered by price.
        Peaked offers can not be accepted or rejected and they do not
        expire.

        Args:
            good:
                the good which should be retrieved
                descending(bool, default=False):
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
        ret = (self.peak_buy_offers(good, sorted=False, descending=False, shuffled=False) +
               self.peak_sell_offers(good, sorted=False, descending=False, shuffled=False))
        if shuffled:
            random.shuffle(ret)
        if sorted:
            ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def sell(self, receiver,
             good, quantity, price, currency='money', epsilon=epsilon):
        """ Sends a offer to sell a particular good to somebody. The amount promised
        is reserved. (self.free(good), shows the not yet reserved goods)

        Args:
            receiver:
                the receiving agent

            'good':
                name of the good

            quantity:
                maximum units disposed to buy at this price

            price:
                price per unit

            currency:
                is the currency of this transaction (defaults to 'money')

            epsilon (optional):
                if you have floating point errors, a quantity or prices is
                a fraction of number to high or low. You can increase the
                floating point tolerance. See troubleshooting -- floating point problems

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
        assert price > - epsilon, 'price %.30f is smaller than 0 - epsilon (%.30f)' % (price, - epsilon)
        if price < 0:
            price = 0
        # makes sure the quantity is between zero and maximum available, but
        # if its only a little bit above or below its set to the bounds
        assert quantity > - epsilon, 'quantity %.30f is smaller than 0 - epsilon (%.30f)' % (quantity, - epsilon)
        if quantity < 0:
            quantity = 0

        self._inventory.reserve(good, quantity)

        offer_id = self._offer_counter()
        offer = Offer(self.name,
                      receiver,
                      good,
                      quantity,
                      price,
                      currency,
                      True,
                      offer_id,
                      self.round)
        self.given_offers[offer_id] = offer
        self._send(receiver[0], receiver[1], '!s', offer)
        return offer

    def buy(self, receiver, good,
            quantity, price, currency='money', epsilon=epsilon):
        """ Sends a offer to buy a particular good to somebody. The money promised
        is reserved. (self.free(currency), shows the not yet reserved goods)

        Args:
            receiver:
                The name of the receiving agent a tuple (group, id).
                e.G. ('firm', 15)

            'good':
                name of the good

            quantity:
                maximum units disposed to buy at this price

            price:
                price per unit

            currency:
                is the currency of this transaction (defaults to 'money')

            epsilon (optional):
                if you have floating point errors, a quantity or prices is
                a fraction of number to high or low. You can increase the
                floating point tolerance. See troubleshooting -- floating point problems
        """
        assert price > - epsilon, 'price %.30f is smaller than 0 - epsilon (%.30f)' % (price, - epsilon)
        if price < 0:
            price = 0
        money_amount = quantity * price
        # makes sure the money_amount is between zero and maximum available, but
        # if its only a little bit above or below its set to the bounds
        available = self._inventory[currency]
        assert money_amount > - epsilon, '%s (price * quantity) %.30f is smaller than 0 - epsilon (%.30f)' % (currency, money_amount, - epsilon)
        if money_amount < 0:
            money_amount = 0
        if money_amount > available:
            money_amount = available

        offer_id = self._offer_counter()
        self._inventory.reserve(currency, money_amount)
        offer = Offer(self.name,
                      receiver,
                      good,
                      quantity,
                      price,
                      currency,
                      False,
                      offer_id,
                      self.round)
        self._send(receiver[0], receiver[1], '!b', offer)
        self.given_offers[offer_id] = offer
        return offer

    def accept(self, offer, quantity=-999, epsilon=epsilon):
        """ The buy or sell offer is accepted and cleared. If no quantity is
        given the offer is fully accepted; If a quantity is given the offer is
        partial accepted.

        Args:

            offer:
                the offer the other party made
            quantity:
                quantity to accept. If not given all is accepted

            epsilon (optional):
                if you have floating point errors, a quantity or prices is
                a fraction of number to high or low. You can increase the
                floating point tolerance. See troubleshooting -- floating point problems

        Return:
            Returns a dictionary with the good's quantity and the amount paid.
        """
        offer_quantity = offer.quantity
        if quantity == -999:
            quantity = offer_quantity
        assert quantity > - epsilon, 'quantity %.30f is smaller than 0 - epsilon (%.30f)' % (quantity, - epsilon)
        if quantity < 0:
            quantity = 0
        if quantity > offer_quantity + epsilon * max(quantity, offer_quantity):
            raise AssertionError('accepted more than offered %s: %.100f >= %.100f'
                                 % (offer.good, quantity, offer_quantity))
        if quantity > offer_quantity:
            quantity = offer_quantity

        if quantity == 0:
            self.reject(offer)
            return {offer.good: 0, offer.currency: 0}

        money_amount = quantity * offer.price
        if offer.sell:  # ord('s')
            assert money_amount > - epsilon, 'money = quantity * offer.price %.30f is smaller than 0 - epsilon (%.30f)' % (money_amount, - epsilon)
            if money_amount < 0:
                money_amount = 0

            available = self._inventory[offer.currency]
            if money_amount > available + epsilon + epsilon * max(money_amount, available):
                raise NotEnoughGoods(self.name, offer.currency, money_amount - available)
            if money_amount > available:
                money_amount = available
            self._inventory.haves[offer.good] += quantity
            self._inventory.haves[offer.currency] -= quantity * offer.price
        else:
            assert quantity > - epsilon, 'quantity %.30f is smaller than 0 - epsilon (%.30f)' % (quantity, - epsilon)
            if quantity < 0:
                quantity = 0
            available = self._inventory[offer.good]
            if quantity > available + epsilon + epsilon * max(quantity, available):
                raise NotEnoughGoods(self.name, offer.good, quantity - available)
            if quantity > available:
                quantity = available
            self._inventory.haves[offer.good] -= quantity
            self._inventory.haves[offer.currency] += quantity * offer.price
        offer.final_quantity = quantity
        self._send(*offer.sender, '_p', (offer.id, quantity))
        del self._polled_offers[offer.id]
        if offer.sell:
            return {offer.good: - quantity, offer.currency: money_amount}
        else:
            return {offer.good: quantity, offer.currency: - money_amount}

    def _reject_polled_but_not_accepted_offers(self):
        for offer in self._polled_offers.values():
            self._reject(offer)
        self._polled_offers = {}

    def _reject(self, offer):
        """  Rejects the offer offer

        Args:
            offer:
                the offer the other party made
                (offer not quote!)
        """
        self._send(*offer.sender, '_r', offer.id)

    def reject(self, offer):
        """ Rejects and offer, if the offer is subsequently accepted in the
        same subround it is accepted'. Peaked offers can not be rejected.

        Args:

            offer:
                the offer to be rejected
        """
        pass

    def _receive_accept(self, offer_id_final_quantity):
        """ When the other party partially accepted the  money or good is
        received, remaining good or money is added back to haves and the offer
        is deleted
        """
        offer = self.given_offers[offer_id_final_quantity[0]]
        offer.final_quantity = offer_id_final_quantity[1]
        if offer.sell:
            self._inventory.commit(offer.good, offer.quantity, offer.final_quantity)
            self._inventory.haves[offer.currency] += offer.final_quantity * offer.price
        else:
            self._inventory.haves[offer.good] += offer.final_quantity
            self._inventory.commit(offer.currency, offer.quantity * offer.price, offer.final_quantity * offer.price)
        offer.status = "accepted"
        offer.status_round = self.round
        del self.given_offers[offer.id]
        return offer

    def _log_receive_accept_group(self, offer):
        if offer.sell:
            self._trade_log[(offer.good, self.group, offer.receiver_group, offer.price)] += offer.final_quantity
        else:
            self._trade_log[(offer.good, offer.receiver_group, self.group, offer.price)] += offer.final_quantity

    def _log_receive_accept_agent(self, offer):
        if offer.sell:
            self._trade_log[(offer.good, self.name_without_colon, '%s_%i' % (*offer.receiver, offer.price))] += offer.final_quantity
        else:
            self._trade_log[(offer.good, '%s_%i' % (*offer.receiver, self.name_without_colon, offer.price))] += offer.final_quantity

    def _receive_reject(self, offer_id):
        """ delets a given offer

        is used by _msg_clearing__end_of_subround, when the other party rejects
        or at the end of the subround when agent retracted the offer

        """
        offer = self.given_offers[offer_id]
        if offer.sell:
            self._inventory.rewind(offer.good, offer.quantity)
        else:
            self._inventory.rewind(offer.currency, offer.quantity * offer.price)
        offer.status = "rejected"
        offer.status_round = self.round
        offer.final_quantity = 0
        del self.given_offers[offer_id]

    def _delete_given_offer(self, offer_id):
        offer = self.given_offers.pop(offer_id)
        if offer.sell:
            self._inventory.rewind(offer.good, offer.quantity)
        else:
            self._inventory.rewind(offer.currency, offer.quantity * offer.price)

    def give(self, receiver, good, quantity, epsilon=epsilon):
        """ gives a good to another agent

        Args:
            receiver:
                The name of the receiving agent a tuple (group, id).
                e.G. ('firm', 15)
            good:
                the good to be transfered
            quantity:
                amount to be transfered

            epsilon (optional):
                if you have floating point errors, a quantity or prices is
                a fraction of number to high or low. You can increase the
                floating point tolerance. See troubleshooting -- floating point problems

        Raises:

            AssertionError, when good smaller than 0.

        Return:
            Dictionary, with the transfer, which can be used by self.log(...).

        Example::

            self.log('taxes', self.give('money': 0.05 * self['money'])

        """
        assert quantity > - epsilon, 'quantity %.30f is smaller than 0 - epsilon (%.30f)' % (quantity, - epsilon)
        if quantity < 0:
            quantity = 0
        available = self._inventory[good]
        if quantity > available + epsilon + epsilon * max(quantity, available):
            raise NotEnoughGoods(self.name, good, quantity - available)
        if quantity > available:
            quantity = available
        self._inventory.haves[good] -= quantity
        self._send(receiver[0], receiver[1], '_g', [good, quantity])
        return {good: quantity}

    def take(self, receiver, good, quantity, epsilon=epsilon):
        """ take a good from another agent. The other agent has to accept.
        using self.accept()

        Args:


            receiver:
                the receiving agent

            good:
                the good to be taken

            quantity:
                the quantity to be taken

            epsilon (optional):
                if you have floating point errors, a quantity or prices is
                a fraction of number to high or low. You can increase the
                floating point tolerance. See troubleshooting -- floating point problems
        """
        self.buy(receiver[0], receiver[1], good=good, quantity=quantity, price=0, epsilon=epsilon)

    def _clearing__end_of_subround(self, incomming_messages):
        """ agent receives all messages and objects that have been send in this
        subround and deletes the offers that where retracted, but not executed.

        '_o': registers a new offer
        '_d': delete received that the issuing agent retract
        '_p': clears a made offer that was accepted by the other agent
        '_r': deletes an offer that the other agent rejected
        '_g': recive a 'free' good from another party
        """
        for typ, msg in incomming_messages:
            if typ == '!b':
                self._open_offers_buy[msg.good][msg.id] = msg
            elif typ == '!s':
                self._open_offers_sell[msg.good][msg.id] = msg
            elif typ == '_p':
                offer = self._receive_accept(msg)
                if self.trade_logging == 2:
                    self._log_receive_accept_group(offer)
                elif self.trade_logging == 1:
                    self._log_receive_accept_agent(offer)
            elif typ == '_r':
                self._receive_reject(msg)
            elif typ == '_g':
                self._inventory.haves[msg[0]] += msg[1]
            elif typ == '_q':
                self._quotes[msg.id] = msg
            elif typ == '!o':
                self._contract_offers[msg.good].append(msg)
            elif typ == '_ac':
                contract = self._contract_offers_made.pop(msg.id)
                if contract.pay_group == self.group and contract.pay_id == self.id:
                    self._contracts_pay[contract.good][contract.id] = contract
                else:
                    self._contracts_deliver[contract.good][contract.id] = contract
            elif typ == '_dp':
                if msg.pay_group == self.group and msg.pay_id == self.id:
                    self._inventory[msg.good] += msg.quantity
                    self._contracts_pay[msg.good][msg.id].delivered.append(self.round)
                else:
                    self._inventory['money'] += msg.quantity * msg.price
                    self._contracts_deliver[msg.good][msg.id].paid.append(self.round)

            elif typ == '!d':
                if msg[0] == 'r':
                    del self._contracts_pay[msg[1]][msg[2]]
                if msg[0] == 'd':
                    del self._contracts_deliver[msg[1]][msg[2]]
            else:
                self._msgs.setdefault(typ, []).append(msg)


def compare_with_ties(x, y):
    if x < y:
        return -1
    elif x > y:
        return 1
    else:
        return random.randint(0, 1) * 2 - 1
