# pylint: disable=W0232, C1001, C0111, R0913, E1101, W0212
# TODO end_contract; record all payments
from __future__ import print_function
from builtins import str
from builtins import object
from abce.notenoughgoods import NotEnoughGoods
from random import shuffle
from abce.trade import get_epsilon

epsilon = get_epsilon()


class Credit(object):
    __slots__ = ['sender_group', 'sender_id', 'deliver_good_group',
                 'deliver_good_id', 'pay_group', 'pay_id', 'amount', 'interest']

    def __init__(self, sender_group, sender_id, deliver_good_group,
                 deliver_good_id, pay_group, pay_id, quantity, interest):
        self.sender_group = sender_group
        self.sender_id = sender_id
        self.deliver_good_group = deliver_good_group
        self.deliver_good_id = deliver_good_id
        self.pay_group = pay_group
        self.pay_id = pay_id
        self.quantity = quantity
        self.interest = interest
        self.id = id
        self.round = round

    def __str__(self):
        return str(('sender', self.sender_group, self.sender_id, 'deliver', self.deliver_good_group,
                    self.deliver_good_id, self.pay_group, self.pay_id, self.quantity, self.interest))


class Credit(object):
    """ This class implements a bank credit, without a due date

    """

    def request_credit(self, receiver_group, receiver_id, quantity, interest):
        """This method offers a contract to provide a good or service to the
        receiver. For a given time at a given price.

        Args:

            receiver_group:
                group to receive the good
            receiver_id:
                group to receive the good
            quantity:
                original amount to be borrowed
            interest:
                period interest
        """
        offer = Credit(sender_group=self.group,
                       sender_id=self.id,
                       deliver_good_group=self.group,
                       deliver_good_id=self.id,
                       pay_group=receiver_group,
                       pay_id=receiver_id,
                       quantity=quantity,
                       interest=interest)
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
        """ Accepts the contract. The contract is completely accepted, when
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
        # if contract is Credit:

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
        return request_offer

    def contracts_to_receive_all(self):
        ret = {}
        for good in self._contracts_pay:
            ret[good] = list(self._contracts_pay[good].values())
        return request_offer

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


def bound_zero(x):
    """ asserts that variable is above zero, where foating point imprecission is accounted for,
    and than makes sure it is above 0, without floating point imprecission """
    assert x > - \
        epsilon, '%.30f is smaller than 0 - epsilon (%.30f)' % (x, - epsilon)
    if x < 0:
        return 0
    else:
        return x
