from __future__ import division
import abce
from tools import *
from abce import NotEnoughGoods


class ContractBuyer(abce.Agent, abce.Contracting):
    def init(self, simulation_parameters, agent_parameters):
        self.last_round = simulation_parameters['rounds'] - 1
        if self.idn == 0:
            self.create('labor_endowment', 1)

    def request_offer(self):
        if self.idn == 1:
            if self.round % 10 == 0:
                self.given_contract = self.request_good_contract('contractbuyer', 0,
                                                                 'labor',
                                                                 quantity=5,
                                                                 price=10,
                                                                 duration=9)

    def accept_offer(self):
        if self.idn == 0:
            contracts = self.get_contract_offers('labor')
            for contract in contracts:
                self.accepted_contract = self.accept_contract(contract)

    def deliver(self):
        if self.idn == 0:
            self.deliver_contract(self.accepted_contract)
            assert self.possession('labor') == 0

    def pay(self):
        if self.idn == 1:
            if self.was_delivered_this_round(self.given_contract):
                self.create('money', 50)
                self.pay_contract(self.given_contract)
                assert self.possession('money') == 0

    def control(self):
        if self.idn == 1:
            assert self.was_delivered_this_round(self.given_contract), self.given_contract
            assert self.possession('money') == 0
            assert self.possession('labor') == 5
        else:
            assert self.was_paid_this_round(self.accepted_contract), self._contracts_payed
            assert self.possession('labor') == 0, self.possession('labor')
            assert self.possession('money') == 50, self.possession('money')
            self.destroy('money')

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.idn == 0:
            print('Test make_contract_offer\t\t\tOK')
            print('Test get_contract_offer \t\t\tOK')
            print('Test deliver            \t\t\tOK')
            print('Test pay_contract       \t\t\tOK')
            print('Test is_payed    \t\t\t\tOK')
            print('Test is_delivered\t\t\t\tOK')
