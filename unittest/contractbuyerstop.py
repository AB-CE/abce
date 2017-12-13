import abce


class ContractBuyerStop(abce.Agent, abce.Contracting):
    def init(self, rounds):
        self.last_round = rounds - 1
        if self.id == 0:
            self.create('labor_endowment', 1)

    def request_offer(self):
        if self.id == 1:
            if self.round % 10 == 0:
                self.given_contract = self.request_good_contract('contractbuyerstop', 0,
                                                                 'labor',
                                                                 quantity=5,
                                                                 price=10,
                                                                 duration=31)
            if self.round % 5 == 0 and self.round % 10 != 0:
                self.end_contract(self.given_contract)

    def accept_offer(self):
        if self.id == 0:
            contracts = self.get_contract_offers('labor')
            for contract in contracts:
                self.accepted_contract = self.accept_contract(contract)

    def deliver(self):
        for contract in self.contracts_to_deliver('labor'):
            self.deliver_contract(contract)
            assert self['labor'] == 0

    def pay(self):
        for contract in self.contracts_to_receive('labor'):
            if self.was_delivered_this_round(contract):
                self.create('money', 50)
                self.pay_contract(contract)
                assert self['money'] == 0

    def control(self):
        if self.round % 10 < 5:
            if self.id == 1:
                assert self.was_delivered_this_round(
                    self.given_contract), self.given_contract
                assert self['money'] == 0
                assert self['labor'] == 5
            else:
                assert self.was_paid_this_round(
                    self.accepted_contract), self._contracts_payed
                assert self['labor'] == 0, self['labor']
                assert self['money'] == 50, self['money']
                self.destroy('money')
        else:
            if self.id == 1:
                assert self['money'] == 0
                assert self['labor'] == 0
            else:
                assert self['labor'] == 5, self['labor']
                assert self['money'] == 0, self['money']
                self.destroy('labor')

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print('Test request_offer      \t\t\tOK')
            print('Test end_contract       \t\t\tOK')
