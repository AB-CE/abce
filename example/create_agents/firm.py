from __future__ import division
import abce
from household import Household
from random import random


class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.simulation_parameters = simulation_parameters
        self.count = 1
    def add_firm(self):
        self.create_agent(Firm, "firm", parameters=self.simulation_parameters, agent_parameters=random())

    def add_household(self):
        self.create_agent(Household, "household", parameters=self.simulation_parameters, agent_parameters=random())

    def print_id(self):
        #print(self.group, self.id)
        pass

    def receive_message(self):
        messages = self.get_messages('msg')
        assert len(messages) == 1
        assert messages[0].content == self.id

