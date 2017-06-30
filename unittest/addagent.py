from __future__ import division
from abce.agent import Agent
from buy import Buy
from sell import Sell
from give import Give
from messageb import MessageB
from messagea import MessageA
from endowment import Endowment


class AddAgent(Agent):
    def init(self, simulation_parameters, _,):
        self.rounds = simulation_parameters['rounds']

    def add_agent(self):
        self.create_agent(Buy, 'buy', parameters={'rounds': self.rounds})
        self.create_agent(Buy, 'buy', parameters={'rounds': self.rounds})

        self.create_agent(Sell, 'sell', parameters={'rounds': self.rounds})
        self.create_agent(Sell, 'sell', parameters={'rounds': self.rounds})

        self.create_agent(Give, 'give', parameters={'rounds': self.rounds})

        self.create_agent(MessageA, 'messagea', parameters={
                          'rounds': self.rounds})
        self.create_agent(MessageB, 'messageb', parameters={
                          'rounds': self.rounds})

        self.create_agent(Endowment, 'endowment', parameters={
                          'rounds': self.rounds, 'creation': self.round + 1})
