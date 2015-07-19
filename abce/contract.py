

#pylint: disable=W0232, C1001, C0111, R0913, E1101, W0212
from abce.tools import is_zero, is_positive, is_negative, NotEnoughGoods, epsilon
from random import shuffle

class Contract:
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
                    self.given_contract = self.request_contract('contractbuyer', 0, 'labor', 5, 10 , duration=10 - 1)

            def deliver_or_pay(self):
                self.pay_contract('labor')

        class Worker(abce.Agent, abce.Contract):
            def init(self):
                self.create('adult', 1)

            def accept_offer(self):
                contracts = self.get_contract_requests('labor')
                for contract in contracts:
                    self.accepted_contract = self.accept_contract(contract)

            def deliver_or_pay(self):
                self.deliver('labor')

    Firms and workers can check, whether they have been paid/provided with
    labor using the :meth:`is_payed` and :meth:`is_delivered` methods.

    The worker can also initiate the transaction by requesting a contract with
    :meth:`make_contract_offer`.

    """
    def make_contract_offer(self, receiver_group, receiver_idn, good, quantity, price, duration):
        """This method offers a contract to provide a good or service to the
        receiver. For a given time at a given price.

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

        Example::

            self.given_contract = self.make_contract_offer('firm', 1, 'labor', quantity=8, price=10, duration=10 - 1)
        """
        assert quantity >= 0, (quantity, self.round)
        offer = {'sender_group': self.group,
                 'sender_idn': self.idn,
                 'deliver_group': receiver_group,
                 'deliver_idn': receiver_idn,
                 'pay_group': self.group,
                 'pay_idn': self.idn,
                 'good': good,
                 'quantity': quantity,
                 'price': price,
                 'end_date': duration + self.round,
                 'makerequest': 'm',
                 'idn': self._offer_counter()}
        self._send(receiver_group, receiver_idn, '!o', offer)
        return offer['idn']

    def request_contract(self, receiver_group, receiver_idn, good, quantity, price, duration):
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
        assert quantity >= 0, (quantity, self.round)
        offer = {'sender_group': self.group,
                 'sender_idn': self.idn,
                 'deliver_group': self.group,
                 'deliver_idn': self.idn,
                 'pay_group': receiver_group,
                 'pay_idn': receiver_idn,
                 'good': good,
                 'quantity': quantity,
                 'price': price,
                 'end_date': duration + self.round,
                 'makerequest': 'r',
                 'idn': self._offer_counter()}
        self._send(receiver_group, receiver_idn, '!o', offer)
        return offer['idn']

    def get_contract_offers(self, good, descending=False):
        """ Returns all contract offers and removes them. The order
        is randomized.

        Args:
            good:
                the good which should be retrieved
            descending(bool,default=False):
                False for descending True for ascending by price

        Returns:
         list of quotes ordered by price
        """
        ret = []
        for offer_id in self._contract_offers.keys():
            if (self._contract_offers[offer_id]['good'] == good
            and self._contract_offers[offer_id]['makerequest'] == 'm'):
                ret.append(self._contract_offers[offer_id])
                del self._contract_offers[offer_id]
        shuffle(ret)
        ret.sort(key=lambda objects: objects['price'], reverse=descending)
        return ret

    def get_contract_requests(self, good, descending=True):
        """ Returns all contract requests and removes them. The order
        is randomized.

        Args:
            good:
                the good which should be retrieved
            descending(bool,default=True):
                False for descending True for ascending by price

        Returns:
         list of quotes ordered by price
        """
        ret = []
        for offer_id in self._contract_offers.keys():
            if (self._contract_offers[offer_id]['good'] == good
            and self._contract_offers[offer_id]['makerequest'] == 'r'):
                ret.append(self._contract_offers[offer_id])
                del self._contract_offers[offer_id]
        shuffle(ret)
        ret.sort(key=lambda objects: objects['price'], reverse=descending)
        return ret

    def accept_contract(self, contract, quantity=None):
        """
        """
        if quantity is not None:
            contract['quantity'] = min(contract['quantity'], quantity)
        if contract['makerequest'] == 'm':
            self._contracts_pay[contract['good']].append(contract)
            self._send(contract['sender_group'], contract['sender_idn'], '+d', contract)
        else:
            self._contracts_deliver[contract['good']].append(contract)
            self._send(contract['sender_group'], contract['sender_idn'], '+p', contract)
        return contract['idn']

    def deliver(self, good):
        for contract in self._contracts_deliver[good]:
            if self._haves[good] < contract['quantity'] - epsilon:
                raise NotEnoughGoods(self.name, good, contract['quantity'] - self._haves[good])
            self._haves[good] -= contract['quantity']
            self._send(contract['deliver_group'], contract['deliver_idn'], '!d', contract)


    def pay_contract(self, good):
        for contract in self._contracts_pay[good]:
            if self._haves['money'] < contract['quantity'] * contract['price'] - epsilon:
                raise NotEnoughGoods(self.name, 'money', contract['quantity'] * contract['price'] - self._haves['money'])
            self._haves['money'] -= contract['quantity'] * contract['price']
            self._send(contract['pay_group'], contract['pay_idn'], '!p', contract)


    def is_delivered(self, contract_idn):
        return contract_idn in self._contracts_delivered

    def is_payed(self, contract_idn):
        return contract_idn in self._contracts_payed

    def contract_delivery_commitments(self, good):
        return sum([contract['quantity'] for contract in self._contracts_deliver[good]])

    def contract_payment_commitments(self, good):
        return sum([contract['quantity'] * contract['price'] for contract in self._contracts_pay[good]])

    def contract_delivery_to_receive(self, good):
        return sum([contract['quantity'] for contract in self._contracts_pay[good]])

    def contract_payment_to_receive(self, good):
        return sum([contract['quantity'] * contract['price'] for contract in self._contracts_deliver[good]])






















