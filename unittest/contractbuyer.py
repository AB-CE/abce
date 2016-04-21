from __future__ import division
import abce
from tools import *
from abce.contract import Contract
from abce import NotEnoughGoods


class ContractBuyer(abce.Agent, Contract):
    def init(self, simulation_parameters, agent_parameters):
        self.last_round = simulation_parameters['rounds'] - 1
        if self.idn == 0:
            self.create('labor_endowment', 1)

    def one(self):
        pass

    def two(self):
        pass

    def three(self):
        pass

    def request_offer(self):
        if self.idn == 1:
            if self.round % 10 == 0:
                self.request_contract('contractbuyer', 0, 'labor', 5, 10, duration=10 - 1)

    def accept_offer(self):
        if self.idn == 0:
            contracts = self.get_contract_requests('labor')
            for contract in contracts:
                self.accepted_contract = self.accept_contract(contract)

    def deliver_or_pay(self):
        if self.idn == 0:
            self.deliver('labor')
            assert self.possession('labor') == 0
        else:
            self.create('money', 50)
            self.pay_contract('labor')
            assert self.possession('money') == 0

    def control(self):
        if self.idn == 1:
            assert self.possession('money') == 0
            assert self.possession('labor') == 5
            assert self.has_delivered('contractbuyer', 0), self._contracts_delivered
        else:
            assert self.possession('labor') == 0
            assert self.possession('money') == 50, self.possession('money')
            assert self.has_payed('contractbuyer', 1), self._contracts_payed
            self.destroy('money', 50)

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
