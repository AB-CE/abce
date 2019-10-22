# pylint: disable=W0232, C1001, C0111, R0913, E1101, W0212
# TODO end_contract; record all payments
from __future__ import print_function
from builtins import str
from builtins import object
from abcEconomics.notenoughgoods import NotEnoughGoods
from random import shuffle
from abcEconomics.trader import get_epsilon
from .contracts import Contracts
from .contracting import Contract

epsilon = get_epsilon()


class Credit(object):
    __slots__ = ['sender_group', 'sender_id', 'deliver_good_group',
                 'deliver_good_id', 'pay_group', 'pay_id', 'amount', 'interest']

    def __init__(self, sender_group, sender_id, deliver_good_group,
                 deliver_good_id, pay_group, pay_id, amount, interest):
        self.sender_group = sender_group
        self.sender_id = sender_id
        self.deliver_good_group = deliver_good_group
        self.deliver_good_id = deliver_good_id
        self.pay_group = pay_group
        self.pay_id = pay_id
        self.amount = amount
        self.interest = interest
        self.id = id
        self.round = round

    def __str__(self):
        return str(('sender', self.sender_group, self.sender_id, 'deliver', self.deliver_good_group,
                    self.deliver_good_id, self.pay_group, self.pay_id, self.amount, self.interest))


class FlexibleContracting(object):
    """ This is a class, that allows you to create contracts. For example a
    work contract. One agent commits to deliver a good or service for a set
    amount of time.

    For example you have a firm and a worker class. 'Labor' is set as a service
    meaning that it lasts not longer than one round and the worker how has an
    adult gets one unit of labor every round see: :meth:`abcEconomics.declare_service`.
    The firm offers a work contract, the worker responds. Every round the
    worker delivers the labor and the firm pays.::

        class Firm(abcEconomics.Agent, abcEconomics.Contract)
            def request_offer(self):
                if self.round % 10 == 0:
                    self.given_contract = self.request_contract('contractbuyer', 0,
                                                                good='labor',
                                                                quantity=5,
                                                                price=10,
                                                                duration=10 - 1)

            def deliver_or_pay(self):
                self.pay_contract('labor')

        class Worker(abcEconomics.Agent, abcEconomics.Contract):
            def init(self):
                self.create('adult', 1)

            def accept_offer(self):
                contracts = self.get_contract_requests('labor')
                for contract in contracts:
                    if contract.price < 5:
                        self.accepted_contract = self.accept_contract(contract)

            def deliver_or_pay(self):
                self.deliver('labor')

    Firms and workers can check, whether they have been paid/provided with
    labor using the :meth:`is_paid` and :meth:`is_delivered` methods.

    The worker can also initiate the transaction by requesting a contract with
    :meth:`make_contract_offer`.

    A contract has the following fields:

                 sender_group:

                 sender_id:

                 deliver_group:

                 deliver_id:

                 pay_group:

                 pay_id:

                 good:

                 quantity:

                 price:

                 end_date:

                 makerequest:
                    'm' for make_contract_offer and 'r' for request_contract

                 id:
                    unique number of contract

    """

    def _add_contracts_list(self):
        self.contracts = Contracts(self.name)

    def request_credit(self, receiver_group, receiver_id,
                       amount, interest, end_date):
        """This method offers a contract to provide a good or service to the
        receiver. For a given time at a given price.

        Args:

            receiver_group:
                group to receive the good
            receiver_id:
                group to receive the good
            deliver:
                an array or function that returns a number or dict for each round,
                the tuple specifies which goods have to be delivered at
                which price.
            receive:
                an array or function that returns a number or a dict for each round,
                the tuple specifies which goods have to be delivered at
                which price.

        Example::

            self.given_contract = self.make_contract_offer('firm', 1, 'labor', quantity=8, price=10, duration=10 - 1)
        """
        offer = Credit(sender_group=self.group,
                       sender_id=self.id,
                       deliver_good_group=self.group,
                       deliver_good_id=self.id,
                       pay_group=receiver_group,
                       pay_id=receiver_id,
                       good='money',
                       quantity=amount,
                       price=interest,
                       end_date=end_date,
                       id=self._offer_counter(),
                       round=self.round)
        self._send(receiver_group, receiver_id, '!o', offer)
        self._contract_offers_made[offer.id] = offer
        return offer

    def request_good_contract(self, receiver_group, receiver_id, good, quantity, price, duration):
        """This method requests a contract to provide a good or service to the
        sender. For a given time at a given price. For example a job
        advertisement.

        Args:

            receiver_group:
                group of the receiver
            receiver_id:
                id of the receiver
            good:
                the good or service that should be provided
            quantity:
                the quantity that should be provided
            price:
                the price of the good or service
            duration:
                the length of the contract, if duration is None or not set,
                the contract has no end date.
        """
        quantity = bound_zero(quantity)
        if duration is None:
            end_date = None
        else:
            end_date = duration + self.round

        offer = Contract(sender_group=self.group,
                         sender_id=self.id,
                         pay_group=self.group,
                         pay_id=self.id,
                         deliver_good_group=receiver_group,
                         deliver_good_id=receiver_id,
                         good=good,
                         quantity=quantity,
                         price=price,
                         end_date=end_date,
                         id=self._offer_counter(),
                         round=self.round)
        self._send(receiver_group, receiver_id, '!o', offer)
        self._contract_offers_made[offer.id] = offer
        return offer

    def get_contract_offers(self, good, descending=False):
        """ Returns all contract offers and removes them. The contract
        are ordered by price (ascending), when tied they are randomized.

        Args:
            good:
                good that underlies the contract

            descending(bool,default=False):
                False for descending True for ascending by price

        Returns:
            list of contract offers ordered by price
        """
        ret = self._contract_offers[good]
        del self._contract_offers[good]
        shuffle(ret)
        ret.sort(key=lambda objects: objects.price, reverse=descending)
        return ret

    def accept_contract(self, contract, quantity=None):
        """ Accepts the contract. The contract is completely aceppted, when
        the quantity is not given. Or partially when quantity is set.

        Args:

            contract:
                the contract in question, received with get_contract_requests or
                get_contract_offers

            quantity (optional):
                the quantity that is accepted. Defaults to all.
        """
        if quantity is None:
            quantity = contract.quantity
        else:
            contract.quantity = min(contract.quantity, quantity)
            assert quantity < contract.quantity + \
                epsilon * max(quantity, contract.quantity)
            if quantity > contract.quantity:
                quantity = contract.quantity

        if contract.pay_group == self.group and contract.pay_id == self.id:
            self._contracts_pay[contract.good][contract.id] = contract
            self._send(contract.sender_group,
                       contract.sender_id, '_ac', contract)
        else:
            self._contracts_deliver[contract.good][contract.id] = contract
            self._send(contract.sender_group,
                       contract.sender_id, '_ac', contract)
        return contract

    def deliver_contract(self, contract):
        """ delivers on a contract """
        assert contract.deliver_good_group == self.group and contract.deliver_good_id == self.id
        quantity = contract.quantity
        available = self._haves[contract.good]
        if quantity > available + epsilon + epsilon * max(quantity, available):
            raise NotEnoughGoods(self.name, contract.good,
                                 quantity - available)
        if quantity > available:
            quantity = available

        self._haves[contract.good] -= quantity
        self._send(contract.pay_group, contract.pay_id, '_dp', contract)

    def pay_contract(self, contract):
        """ delivers on a contract """
        assert contract.pay_group == self.group and contract.pay_id == self.id
        money = contract.quantity * contract.price
        available = self._haves['money']
        if money > available + epsilon + epsilon * max(money, available):
            raise NotEnoughGoods(self.name, 'money', money - available)
        if money > available:
            money = available

        self._haves['money'] -= money
        self._send(contract.deliver_good_group,
                   contract.deliver_good_id, '_dp', contract)

    def contracts_to_deliver(self, good):
        return list(self._contracts_deliver[good].values())

    def contracts_to_receive(self, good):
        return list(self._contracts_pay[good].values())

    def contracts_to_deliver_all(self):
        ret = {}
        for good in self._contracts_deliver:
            ret[good] = list(self._contracts_deliver[good].values())
        return ret

    def contracts_to_receive_all(self):
        ret = {}
        for good in self._contracts_pay:
            ret[good] = list(self._contracts_pay[good].values())
        return ret

    def end_contract(self, contract):
        if contract.id in self._contracts_deliver[contract.good]:
            self._send(contract.pay_group, contract.pay_id,
                       '!d', ('r', contract.good, contract.id))
            del self._contracts_deliver[contract.good][contract.id]
        elif contract.id in self._contracts_pay[contract.good]:
            self._send(contract.deliver_good_group, contract.deliver_good_id,
                       '!d', ('d', contract.good, contract.id))
            del self._contracts_pay[contract.good][contract.id]
        else:
            raise Exception("Contract not found")

    def was_paid_this_round(self, contract):
        return contract.paid[-1] == self.round

    def was_delivered_this_round(self, contract):
        return contract.delivered[-1] == self.round

    def was_paid_last_round(self, contract):
        return self.round - 1 in contract.paid

    def was_delivered_last_round(self, contract):
        return self.round - 1 in contract.delivered

    def calculate_netvalue(self, prices={},
                           parameters={},
                           value_functions={}):
        return (self._haves.calculate_netvalue(prices) +
                self.contracts.calculate_netvalue(parameters, value_functions))

    def calculate_assetvalue(self, prices={},
                             parameters={},
                             value_functions={}):
        return (self._haves.calculate_assetvalue(prices) +
                self.contracts.calculate_assetvalue(parameters,
                                                    value_functions))

    def calculate_liablityvalue(self, prices={},
                                parameters={},
                                value_functions={}):
        return (self._haves.calculate_liablityvalue(prices) +
                self.contracts.calculate_liablityvalue(parameters,
                                                       value_functions))

    def calculate_valued_assets(self, prices={},
                                parameters={},
                                value_functions={}):
        return (self._haves.calculate_valued_assets(prices) +
                self.contracts.calculate_valued_assets(parameters,
                                                       value_functions))

    def calculate_valued_liablities(self, prices={},
                                    parameters={},
                                    value_functions={}):
        return (self._haves.calculate_valued_liablities(prices) +
                self.contracts.calculate_valued_liablities(parameters,
                                                           value_functions))


def bound_zero(x):
    """ asserts that variable is above zero, where foating point imprecission is accounted for,
    and than makes sure it is above 0, without floating point imprecission """
    assert x > - epsilon, \
        '%.30f is smaller than 0 - epsilon (%.30f)' % (x, - epsilon)
    if x < 0:
        return 0
    else:
        return x
