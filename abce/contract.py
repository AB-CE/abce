#pylint: disable=W0232, C1001, C0111, R0913, E1101, W0212
from abce.tools import is_zero, is_positive, is_negative, NotEnoughGoods, epsilon


class Contract:
    def make_contract_offer(self, receiver_group, receiver_idn, good, quantity, price, duration):
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
                 'idn': self._offer_counter()}
        self._send(receiver_group, receiver_idn, '!o', offer)
        return offer['idn']

    def get_contract_offers(self, good, descending=False):
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
        for offer_id in self._contract_offers.keys():
            if self._contract_offers[offer_id]['good'] == good:
                ret.append(self._contract_offers[offer_id])
                del self._contract_offers[offer_id]
        ret.sort(key=lambda objects: objects['price'], reverse=descending)
        return ret

    def accept_contract(self, offer):
        self._contracts_pay[offer['good']].append(offer)
        self._send(offer['sender_group'], offer['sender_idn'], '+d', offer)
        return offer['idn']

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
