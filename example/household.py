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
        if self.count('red_ball') > 0:
            self.sell(reciever, "red_ball", self.count('red_ball'), 1)

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
        return slapp.agent_name('agent', (1 + self.idn) % HARDCODEDNUMBEROFAGENTS)

Start methods that start are not meant to be in the self.action with an
underscore('_'), this makes the execution faster as the system does not have
to keep track whether this methods are externally called.
"""
from agentengine import *
import random


class Household(AgentEngine, Household):
    """ The Agent class contains and registers agents actions. """
    def __init__(self, world_parameters, own_parameters, _pass_to_engine):
        AgentEngine.__init__(self, *_pass_to_engine)
        self.create('labor_endowment', 1)
        self.create('capital_endowment', 1)
        self.set_cobb_douglas_utility_function(1.980, {"MLK": 0.300, "BRD": 0.700})
        self._prices = {}
        self._prices['labor'] = 1
        self.employer = random.randint(0, world_parameters['number_of_firms'])
        self.number_of_firms = world_parameters['number_of_firms']
        self.renter = random.randint(0, 100)
        self.last_utility = None


    def recieve_connections(self):
        self.potential_buyer = self.get_messages('address')

    def offer_labor(self):
        self._prices['labor'] = random.randint(0,3)
        self.quote_sell(agent_name('firm', self.employer), 'labor', 1000, self._prices['labor'])

    def accept_job_offer(self):
        offers = self.open_offers_all()
        if offers:
            offers = sort(offers,'price', reverse=True)
            try:
                self.accept(offers[0])
                pass
            except GoodDoesNotExist:
                print('no')

    def offer_capital(self):
        if self.potential_buyer:  #TODO del
            self.sell(self.potential_buyer[0], "capital", 2, 1)

    def buy_good(self):
        offers = self.open_offers('BRD')
        if offers:
            self.accept(random.choice(offers))
        offers = self.open_offers('MLK')
        if offers:
            self.accept(random.choice(offers))

    def consumption(self):
        try:
            self.last_utility = self.consume_everything()
        except GoodDoesNotExist:
            pass

    def follow(self):
        track = {}
        track.update(self._haves)
        track['utility'] = self.last_utility
        return track