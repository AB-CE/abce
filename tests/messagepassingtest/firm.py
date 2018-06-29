from __future__ import division
import abcEconomics


class Firm(abcEconomics.Agent, abcEconomics.Firm):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.num_households = simulation_parameters['households']
        self.num_firms = simulation_parameters['firms']
        print(self.name)

    def one(self):
        self.message('household', self.id, 'hello', 'ping %i' % self.round)
        self.message('firm', self.num_firms - self.id -
                     1, 'hello', 'ping %i' % self.round)
        self.create('cookies', self.id)
        #self.sell('household', self.id, good='cookies', quantity=min(self.id, 2), price=1)

    def two(self):
        messages = self.get_messages("hello")
        print('-', self.name, messages)
        print(self.name, 'money', self.possession('money'))
