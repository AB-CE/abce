#ABCE 0.1
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
        return agent_name('agent', (1 + self.idn) % HARDCODEDNUMBEROFAGENTS)

Start methods that start are not meant to be in the self.action with an
underscore('_'), this makes the execution faster as the system does not have
to keep track whether this methods are externally called.
"""
from agentengine import *


class Agent(AgentEngine, Firm, Household):
    """ The Agent class contains agents actions.
    if your agent is a Firm, meaning it uses production functions it must inherit from firm::

     class Agent(AgentEngine, Firm):

    if it is a utility maximizing household::

     class Agent(AgentEngine, Household):
    """
    def __init__(self, parameter, arguments):
        """ all parameters in parameter.csv can be accessed in the agent's
        __init__(...) function. parameter['column name']. For example:

        self.number_of_firms = parameter['number_of_firms']
        """
        AgentEngine.__init__(self, *arguments)
