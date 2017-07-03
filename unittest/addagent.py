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
        self.create_agent(Buy, parameters={'rounds': self.rounds})
        self.create_agent(Buy, parameters={'rounds': self.rounds})

        self.create_agent(Sell, parameters={'rounds': self.rounds})
        self.create_agent(Sell, parameters={'rounds': self.rounds})

        self.create_agent(Give, parameters={'rounds': self.rounds})

        self.create_agent(MessageA, parameters={
                          'rounds': self.rounds})
        self.create_agent(MessageB, parameters={
                          'rounds': self.rounds})

        self.create_agent(Endowment, parameters={
                          'rounds': self.rounds, 'creation': self.round + 1})
