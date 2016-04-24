#pylint: disable=W0232, C1001, C0111, R0913, E1101, W0212
# TODO end_contract; record all payments
from abce.notenoughgoods import NotEnoughGoods
from random import shuffle
from copy import deepcopy
from abce.trade import get_epsilon
from numpy import isfinite

epsilon = get_epsilon()


class Contract(object):
    __slots__ = ['sender_group', 'sender_idn', 'deliver_good_group',
                 'deliver_good_idn', 'pay_group', 'pay_idn', 'good', 'quantity',
                 'price', 'end_date', 'delivered', 'paid', 'idn']
    def __init__(self, sender_group, sender_idn, deliver_good_group,
                 deliver_good_idn, pay_group, pay_idn, good, quantity, price,
                 end_date, idn):
        self.sender_group = sender_group
        self.sender_idn = sender_idn
        self.deliver_good_group = deliver_good_group
        self.deliver_good_idn = deliver_good_idn
        self.pay_group = pay_group
        self.pay_idn = pay_idn
        self.good = good
        self.quantity = quantity
        self.price = price
        self.end_date = end_date
        self.delivered = None
        self.paid = None
        self.idn = idn

    def __str__(self):
        return str(self.__dict__)

class Contracting:
    """ This is a class, that allows you to create contracts. For example a
    work contract. One agent commits to deliver a good or service for a set
    amount of time.

    For example you have a firm and a worker class. 'Labor' is set as a service
    meaning that it lasts not longer than one round and the worker how has an
    adult gets one unit of labor every round see: :meth:`abce.declare_service`.
    The firm offers a work contract, the worker responds. Every round the
    worker delivers the labor and the firm pays.::

        class Firm(abce.Agent, abce.Contract)
            def request_offer(self):
                if self.round % 10 == 0:
                    self.given_contract = self.request_contract('contractbuyer', 0,
                                                                good='labor',
                                                                quantity=5,
                                                                price=10,
                                                                duration=10 - 1)

            def deliver_or_pay(self):
                self.pay_contract('labor')

        class Worker(abce.Agent, abce.Contract):
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

                 sender_idn:

                 deliver_group:

                 deliver_idn:

                 pay_group:

                 pay_idn:

                 good:

                 quantity:

                 price:

                 end_date:

                 makerequest:
                    'm' for make_contract_offer and 'r' for request_contract

                 idn:
                    unique number of contract

    """
    def offer_good_contract(self, receiver_group, receiver_idn, good, quantity, price, duration):
        """This method offers a contract to provide a good or service to the
        receiver. For a given time at a given price.

        Args:

            receiver_group:
                group to receive the good
            receiver_idn:
                group to receive the good
            good:
                the good or service that should be provided
            quantity:
                the quantity that should be provided
            price:
                the price of the good or service
            duration:
                the lenght of the contract

        Example::

            self.given_contract = self.make_contract_offer('firm', 1, 'labor', quantity=8, price=10, duration=10 - 1)
        """
        quantity = bound_zero(quantity)
        offer = Contract(sender_group = self.group,
                         sender_idn = self.idn,
                         deliver_good_group = self.group,
                         deliver_good_idn = self.idn,
                         pay_group = receiver_group,
                         pay_idn = receiver_idn,
                         good = good,
                         quantity = quantity,
                         price = price,
                         end_date = duration + self.round,
                         idn = self._offer_counter())
        self._send(receiver_group, receiver_idn, '!o', offer)
        self._contract_offers_made[offer.idn] = offer
        return offer

    def request_good_contract(self, receiver_group, receiver_idn, good, quantity, price, duration):
        """This method requests a contract to provide a good or service to the
        sender. For a given time at a given price. For example a job
        advertisement.

        Args:

            receiver_group:
                group of the receiver
            receiver_idn:
                id of the receiver
            good:
                the good or service that should be provided
            quantity:
                the quantity that should be provided
            price:
                the price of the good or service
            duration:
                the lenght of the contract
        """
        quantity = bound_zero(quantity)
        offer = Contract(sender_group = self.group,
                         sender_idn = self.idn,
                         pay_group = self.group,
                         pay_idn = self.idn,
                         deliver_good_group = receiver_group,
                         deliver_good_idn = receiver_idn,
                         good = good,
                         quantity = quantity,
                         price = price,
                         end_date = duration + self.round,
                         idn = self._offer_counter())
        self._send(receiver_group, receiver_idn, '!o', offer)
        self._contract_offers_made[offer.idn] = offer
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
        if quantity is not None:
            contract.quantity = min(contract.quantity, quantity)
        else:
            assert quantity < contract.quantity + epsilon * max(quantity, contract.quantity)
        if quantity > contract.quantity:
            quantity = contract.quantity

        if contract.pay_group == self.group and contract.pay_idn == self.idn:
            self._contracts_pay[contract.good][contract.idn] = contract
            self._send(contract.sender_group, contract.sender_idn, '_ac', contract)
        else:
            self._contracts_deliver[contract.good][contract.idn] = contract
            self._send(contract.sender_group, contract.sender_idn, '_ac', contract)
        return contract

    def deliver_contract(self, contract):
        """ delivers on a contract """
        assert contract.deliver_good_group == self.group and contract.deliver_good_idn == self.idn
        quantity = contract.quantity
        available = self._haves[contract.good]
        if quantity > available + epsilon + epsilon * max(quantity, available):
            raise NotEnoughGoods(self.name, contract.good, quantity - available)
        if quantity > available:
            quantity = available

        self._haves[contract.good] -= quantity
        self._send(contract.pay_group, contract.pay_idn, '_dp', contract)


    def pay_contract(self, contract):
        """ delivers on a contract """
        assert contract.pay_group == self.group and contract.pay_idn == self.idn
        money = contract.quantity * contract.price
        available = self._haves['money']
        if money > available + epsilon + epsilon * max(money, available):
            raise NotEnoughGoods(self.name, 'money', money - available)
        if money > available:
            money = available

        self._haves['money'] -= money
        self._send(contract.deliver_good_group, contract.deliver_good_idn, '_dp', contract)

    def contracts_to_deliver(self, good):
        return self._contracts_deliver[good]

    def contracts_to_receive(self, good):
        return self._contracts_pay[good]

    def contracts_to_deliver_all(self):
        return self._contracts_deliver

    def contracts_to_receive_all(self):
        return self._contracts_pay

    def end_contract(self, contract):
        if contract.idn in self._contracts_deliver[contract.good]:
            self._send(contract.pay_group, contract.pay_idn, '!d', ('r', contract.good, contract.idn))
            del self._contracts_deliver[contract.good][contract.idn]
        elif contract.idn in self._contracts_pay:
            self._send(contract.deliver_group, contract.deliver_idn, '!d', ('d', contract.good, contract.idn))
            del self._contracts_pay[contract.good][contract.idn]
        else:
            raise Exception("Contract not found")

    def was_paid_this_round(self, contract):
        return contract.paid == self.round

    def was_delivered_this_round(self, contract):
        return contract.delivered == self.round

    def was_paid_last_round(self, contract):
        return contract.paid == self.round - 1

    def was_delivered_last_round(self, contract):
        return contract.delivered == self.round - 1

def bound_zero(x):
    """ asserts that variable is above zero, where foating point imprecission is accounted for,
    and than makes sure it is above 0, without floating point imprecission """
    assert x > - epsilon, '%.30f is smaller than 0 - epsilon (%.30f)' % (x, - epsilon)
    if not isfinite(x):
        print 'warning infinity in trade'
    if x < 0:
        return 0
    else:
        return x













