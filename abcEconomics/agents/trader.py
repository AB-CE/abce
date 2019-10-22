# cython: infer_types=True
# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# abcEconomics is open-source software. If you are using abcEconomics for your research you are
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
The :class:`abcEconomics.Agent` class is the basic class for creating your agent. It automatically handles the
possession of goods of an agent. In order to produce/transforme goods you need to also subclass
the :class:`abcEconomics.Firm` [1]_ or to create a consumer the :class:`abcEconomics.Household`.

For detailed documentation on:

Trading:
    see :class:`abcEconomics.Trade`
Logging and data creation:
    see :class:`abcEconomics.Database` and :doc:`simulation_results`
Messaging between agents:
    see :class:`abcEconomics.Messenger`.

.. autoexception:: abcEconomicstools.NotEnoughGoods

.. [1] or :class:`abcEconomics.FirmMultiTechnologies` for simulations with complex technologies.
"""
#******************************************************************************************#
# trade.pyx is written in cython. When you modify trade.pyx you need to compile it with    #
# compile.sh and compile.py because the resulting trade.c file is distributed.             #
# Don't forget to commit it to git                                                         #
#******************************************************************************************#
import random
from collections import defaultdict, OrderedDict
from abcEconomics.notenoughgoods import NotEnoughGoods

epsilon = 0.00000000001


def get_epsilon():
    return epsilon


def fmax(a, b):
    if a > b:
        return a
    else:
        return b


class Offer:
    """ This is an offer container that is send to the other agent. You can
    access the offer container both at the receiver as well as at the sender,
    if you have saved the offer. (e.G. self.offer = self.sell(...))

    it has the following properties:
        sender:
            this is the name of the sender

        receiver:
            This is the name of the receiver

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
                 sell, status, final_quantity, id,
                 made, status_round):
        self.sender = sender
        self.receiver = receiver
        self.good = good
        self.currency = currency
        self.quantity = quantity
        self.price = price
        self.sell = sell
        self.status = status
        self.final_quantity = final_quantity
        self.id = id
        self.made = made
        self.status_round = status_round

    def __reduce__(self):
        return (rebuild_offer, (self.sender, self.receiver, self.good, self.quantity, self.price, self.currency,
                self.sell, self.status, self.final_quantity, self.id,
                self.made, self.status_round))

    def __repr__(self):
        final_quantity = str(self.final_quantity)  # to anticipate for the case when it is None
        status_round = str(self.status_round)  # to anticipate for the case when it is None
        return """<{sender: %s, receiver_group: %s, good: %s, quantity: %f, price: %f, currency: %s,
                sell: %r, status: %s, final_quantity: %s, id: %i,
                made: %i, status_round: %s }>""" % (

            self.sender, self.receiver, self.good, self.quantity, self.price, self.currency,
            self.sell, self.status, final_quantity, self.id,
            self.made, status_round)


def rebuild_offer(sender, receiver, good, quantity, price,
                  currency, sell, status, final_quantity,
                  id, made, status_round):
    return Offer(sender, receiver, good, quantity, price, currency,
                 sell, status, final_quantity, id,
                 made, status_round)


class Trader:
    """ Agents can trade with each other. The clearing of the trade is taken care
    of fully by abcEconomics.
    Selling a good works in the following way:

    1. An agent sends an offer. :meth:`~.sell`

       *The good offered is blocked and self.possession(...) does shows the decreased amount.*

    2. **Next subround:** An agent receives the offer :meth:`~.get_offers`, and can
       :meth:`~.accept`, :meth:`~.reject` or partially accept it. :meth:`~.accept`

       *The good is credited and the price is deducted from the agent's possessions.*

    3. **Next subround:**

       - in case of acceptance *the money is automatically credited.*
       - in case of partial acceptance *the money is credited and part of the blocked good is unblocked.*
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
    def __init__(self, id, agent_parameters, simulation_parameters):
        super(Trader, self).__init__(id, agent_parameters, simulation_parameters)
        # unpack simulation_parameters
        trade_logging = simulation_parameters['trade_logging']

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
            self.database_connection.put(["trade_log", self._trade_log, self.time])
        self._trade_log = defaultdict(int)

    def get_buy_offers_all(self, descending=False, sorted=True):
        goods = list(self._open_offers_buy.keys())
        return {good: self.get_offers(good, descending, sorted) for good in goods}

    def get_sell_offers_all(self, descending=False, sorted=True):
        goods = list(self._open_offers_sell.keys())
        return {good: self.get_offers(good, descending, sorted) for good in goods}

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

            a dictionary with good types as keys and list of :class:`abcEconomics.trade.Offer`
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
            print(offer.price, offer.sender_group, offer.sender_id)
        """
        goods = list(self._open_offers_sell.keys()) + list(self._open_offers_buy.keys())
        return {good: self.get_offers(good, descending, sorted) for good in goods}

    def get_buy_offers(self, good, sorted=True, descending=False, shuffled=True):
        ret = list(self._open_offers_buy[good].values())
        self._polled_offers.update(self._open_offers_buy[good])
        del self._open_offers_buy[good]
        if shuffled:
            random.shuffle(ret)
        if sorted:
            ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def get_sell_offers(self, good, sorted=True, descending=False, shuffled=True):
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
            A list of :class:`abcEconomics.trade.Offer` ordered by price.

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
        ret = []
        for offer in self._open_offers_buy[good].values():
            ret.append(offer)
        if shuffled:
            random.shuffle(ret)
        if sorted:
            ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def peak_sell_offers(self, good, sorted=True, descending=False, shuffled=True):
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
        """ commits to sell the quantity of good at price

        The good is not available for the agent. When the offer is
        rejected it is automatically re-credited. When the offer is
        accepted the money amount is credited. (partial acceptance
        accordingly)

        Args:
            receiver_group:
                group of the receiving agent

            receiver_id:
                number of the receiving agent

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
        available = self._inventory[good]
        assert quantity > - epsilon, 'quantity %.30f is smaller than 0 - epsilon (%.30f)' % (quantity, - epsilon)
        if quantity < 0:
            quantity = 0
        if quantity > available + epsilon + epsilon * fmax(quantity, available):
            raise NotEnoughGoods(self.name, good, quantity - available)
        if quantity > available:
            quantity = available

        offer_id = self._offer_counter()
        self._inventory.reserve(good, quantity)
        offer = Offer(self.name,
                      receiver,
                      good,
                      quantity,
                      price,
                      currency,
                      True,
                      'new',
                      -2,
                      offer_id,
                      self.time,
                      -2)
        self.given_offers[offer_id] = offer
        self.send(receiver, 'abcEconomics_propose_sell', offer)
        return offer

    def buy(self, receiver, good,
            quantity, price, currency='money', epsilon=epsilon):
        """ commits to sell the quantity of good at price

        The goods are not in haves or self.count(). When the offer is
        rejected it is automatically re-credited. When the offer is
        accepted the money amount is credited. (partial acceptance
        accordingly)

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
        # makes sure the money_amount is between zero and maximum available, but
        # if its only a little bit above or below its set to the bounds
        available = self._inventory[currency]
        assert quantity > - epsilon, '%s quantity %.30f is smaller than 0 - epsilon (%.30f)' % (currency, quantity, - epsilon)
        if quantity < 0:
            quantity = 0
        money_amount = quantity * price
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
                      'new',
                      -1,
                      offer_id,
                      self.time,
                      -1)
        self.send(receiver, 'abcEconomics_propose_buy', offer)
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
        if quantity > offer_quantity + epsilon * fmax(quantity, offer_quantity):
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
        self.send(offer.sender, 'abcEconomics_receive_accept', (offer.id, quantity))
        del self._polled_offers[offer.id]
        if offer.sell:  # ord('s')
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
        self.send(offer.sender, 'abcEconomics_receive_reject', offer.id)

    def reject(self, offer):
        """ Rejects and offer, if the offer is subsequently accepted in the
        same subround it is accepted'. Peaked offers can not be rejected.

        Args:

            offer:
                the offer to be rejected
        """
        pass

    def _log_receive_accept_group(self, offer):
        if offer.sell:
            self._trade_log[(offer.good, self.group, offer.receiver[0], offer.price)] += offer.quantity
        else:
            self._trade_log[(offer.good, offer.receiver[0], self.group, offer.price)] += offer.quantity

    def _log_receive_accept_agent(self, offer):
        if offer.sell:
            self._trade_log[(offer.good, self.name_without_colon, '%s_%i' % (
                offer.receiver[0], offer.receiver[1]), offer.price)] += offer.quantity
        else:
            self._trade_log[(offer.good, '%s_%i' % (
                offer.receiver[0], offer.receiver[1]), self.name_without_colon, offer.price)] += offer.quantity

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
        offer.status_round = self.time
        del self.given_offers[offer.id]
        return offer

    def _log_receive_accept_group(self, offer):
        if offer.sell:
            self._trade_log[(offer.good, self.group, offer.receiver[0], offer.price)] += offer.quantity
        else:
            self._trade_log[(offer.good, offer.receiver[0], self.group, offer.price)] += offer.quantity

    def _log_receive_accept_agent(self, offer):
        if offer.sell:
            self._trade_log[(offer.good, self.name_without_colon, '%s_%i' % (
                offer.receiver[0], offer.receiver[1]), offer.price)] += offer.quantity
        else:
            self._trade_log[(offer.good, '%s_%i' % (
                offer.receiver[0], offer.receiver[1]), self.name_without_colon, offer.price)] += offer.quantity

    def _receive_reject(self, offer_id):
        """ deletes a given offer

        is used by _do_message_clearing, when the other party rejects
        or at the end of the subround when agent retracted the offer

        """
        offer = self.given_offers[offer_id]
        if offer.sell:
            self._inventory.rewind(offer.good, offer.quantity)
        else:
            self._inventory.rewind(offer.currency, offer.quantity * offer.price)
        offer.status = "rejected"
        offer.status_round = self.time
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

            self.log('taxes', self.give('money': 0.05 * self.possession('money'))

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
        self.send(receiver, 'abcEconomics_receive_good', [good, quantity])
        return {good: quantity}

    def take(self, receiver, good, quantity, epsilon=epsilon):
        """ take a good from another agent. The other agent has to accept.
        using self.accept()

        Args:


            receiver_group:
                group of the receiving agent

            receiver_id:
                number of the receiving agent

            good:
                the good to be taken

            quantity:
                the quantity to be taken

            epsilon (optional):
                if you have floating point errors, a quantity or prices is
                a fraction of number to high or low. You can increase the
                floating point tolerance. See troubleshooting -- floating point problems
        """
        self.buy(receiver, good=good, quantity=quantity, price=0, epsilon=epsilon)


# TODO when cython supports function overloading overload this function with compare_with_ties(int x, int y)
def compare_with_ties(x, y):
    if x < y:
        return -1
    elif x > y:
        return 1
    else:
        return random.randint(0, 1) * 2 - 1
