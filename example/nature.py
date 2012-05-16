"""
The Agent class contains and registers an agents actions. Actions need to be
registerd in order to be accessable from outside the class.
When actions are in this class and registered they need to be called in the
ModelSwarm class.

Example::

class Agent(AgentEngine):
    def __init__(self, arguments):
        AgentEngine.__init__(self, *arguments)
        self.create('red_ball', self.idn)
        self.create('money', 10)
        self.red_to_blue = create_production_function('blue_ball=red_ball')
        if self.idn == 0:
            self.painter = True
        else:
            self.painter = False
        self.report()
        HARDCODEDNUMBEROFAGENTS = 3  #hardcoding only for a simple example

    def give(self):
        # gives self.some_agent_name 1 ball, if he has one
        receiver = self.next_agent()
        if self.count('red_ball') > 0:
            self.sell(receiver, "red_ball", self.count('red_ball'), 1)

    def get(self):
        # accepts all balls #
        offers = self.received_offers

        if offers:
            offer = offers.values()[0]
            try:
                self.accept(offer)
            except NotEnoughGoods:
                pass

    def report(self):
        print(self.idn, ':', "have", self.count('blue_ball'), "blue balls", self.count('red_ball'), "red balls", self.count('money') , "$")

    def next_agent(self):
        return agent_name('agent', (1 + self.idn) % HARDCODEDNUMBEROFAGENTS)

Start methods that start are not meant to be in the self.action with an
underscore('_'), this makes the execution faster as the system does not have
to keep track whether this methods are externally called.
"""
from agentengine import *
import random


class Nature(AgentEngine):
    """ The Agent class contains and registers agents actions. """
    def __init__(self, world_parameter, own_parameters, _pass_to_engine):
        AgentEngine.__init__(self, *_pass_to_engine)

    def assign(self):
        """ randomly pairs one household with one firm
        by sending a firm_id to each household
        """
        household_list = range(10)  #TODO
        random_household_list = household_list
        random.shuffle(random_household_list)

        firm_list = range(10)
        random_firm_list = firm_list
        random.shuffle(random_firm_list)
        for hh in household_list:
            receiver = agent_name('household', hh)
            self.send_address(receiver, agent_name('firm', random_firm_list[hh]))
        for firm in firm_list:
            receiver = agent_name('firm', firm)
            self.send_address(receiver, agent_name('household', random_household_list[firm]))
        for firm in firm_list:
            receiver = agent_name('firm', firm)
            self.send_address(receiver, agent_name('household', random_household_list[9 - firm]))

    def recieve_connections(self):
        pass
