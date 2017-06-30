from __future__ import division
from __future__ import print_function
import abce
from tools import *


class ContractBuyerStop(abce.Agent, abce.Contracting):
    def init(self, simulation_parameters, agent_parameters):
        self.last_round = simulation_parameters['rounds'] - 1
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
            assert self.possession('labor') == 0

    def pay(self):
        for contract in self.contracts_to_receive('labor'):
            if self.was_delivered_this_round(contract):
                self.create('money', 50)
                self.pay_contract(contract)
                assert self.possession('money') == 0

    def control(self):
        if self.round % 10 < 5:
            if self.id == 1:
                assert self.was_delivered_this_round(
                    self.given_contract), self.given_contract
                assert self.possession('money') == 0
                assert self.possession('labor') == 5
            else:
                assert self.was_paid_this_round(
                    self.accepted_contract), self._contracts_payed
                assert self.possession('labor') == 0, self.possession('labor')
                assert self.possession('money') == 50, self.possession('money')
                self.destroy('money')
        else:
            if self.id == 1:
                assert self.possession('money') == 0
                assert self.possession('labor') == 0
            else:
                assert self.possession('labor') == 5, self.possession('labor')
                assert self.possession('money') == 0, self.possession('money')
                self.destroy('labor')

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print('Test request_offer      \t\t\tOK')
            print('Test end_contract       \t\t\tOK')
