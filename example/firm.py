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
        reciever = self.next_agent()
        if self.create('red_ball') > 0:
            self.sell(reciever, "red_ball", self.create('red_ball'), 1)

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
        print(self.idn, ':', "have", self.create('blue_ball'), "blue balls", self.create('red_ball'), "red balls", self.create('money') , "$")

    def next_agent(self):
        return slapp.agent_name('agent', (1 + self.idn) % HARDCODEDNUMBEROFAGENTS)

Start methods that start are not meant to be in the self.action with an
underscore('_'), this makes the execution faster as the system does not have
to keep track whether this methods are externally called.
"""
from agentengine import *
from random import choice

class Firm(AgentEngine, Firm):
    """ The Agent class contains and registers agents actions. """
    def __init__(self, world_parameter, own_parameters, _pass_to_engine):
        AgentEngine.__init__(self, *_pass_to_engine)
        self.create('money', 1000000)
        if self.idn < 5:
            self.set_cobb_douglas('BRD', 1.890, {"capital": 0.333, "labor": 0.667})
            self.output = 'BRD'
        if self.idn >= 5:
            self.set_cobb_douglas("MLK", 1.980, {"capital": 0.571, "labor": 0.492})
            self.output = 'MLK'
        self.capacity = 10
        potential_buyer = {}

    def recieve_connections(self):
        self.potential_buyer = self.get_messages('address')

    def buy_capital(self):
        offers = self.open_offers('capital')
        if offers:
            self.accept(choice(offers))

    def hire_labor(self):
        quotes = list(self.get_quotes())
        if quotes:
            quotes = sort(quotes, 'price')[0:self.capacity]
            for quote in quotes:
                self.accept_quote(quote)

    def production(self):
        try:
            self.produce({'labor': self.possession('labor'), 'capital': self.possession('capital')})
        except GoodDoesNotExist:
            pass

    def sell_good(self):
        for pb in self.potential_buyer:
            try:
                self.sell(pb, self.output, 1, 1)
            except GoodDoesNotExist:
                pass
            except NotEnoughGoods:
                pass
