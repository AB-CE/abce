""" 1. declared the timeline
    2. build one Household and one Firm follow_agent
    3. For every labor_endowment an agent has he gets one trade or usable labor
    per round. If it is not used at the end of the round it disapears.
    4. Firms' and Households' possesions are monitored ot the points marked in
    timeline.
"""

from __future__ import division
from abce import Simulation, gui
from firm import Firm
from household import Household
import abce

parameters = {'name': '2x2',
              'random_seed': None,
              'rounds': 10}

class Household(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        """ 1. labor_endowment, which produces, because of w.declare_resource(...)
        in start.py one unit of labor per month
        2. Sets the utility function to utility = consumption of good "GOOD"
        """
        self.create('adult', 1)
        self.set_cobb_douglas_utility_function({"GOOD": 1})
        self.current_utiliy = 0
    def sell_labor(self):
        """ offers one unit of labor to firm 0, for the price of 1 "money" """
        self.sell('firm', 0, good="labor", quantity=1, price=1)
    def buy_goods(self):
        """ receives the offers and accepts them one by one """
        self.accept_offers("GOOD")
    def consumption(self):
        """ consumes_everything and logs the aggregate utility. current_utiliy
        """
        self.current_utiliy = self.consume_everything()
        self.log_value('HH', self.current_utiliy)

class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        """ 1. Gets an initial amount of money
            2. create a cobb_douglas function: GOOD = 1 * labor ** 1.
        """
        self.create('money', 1)
        self.set_cobb_douglas({"GOOD": 1}, {"labor": 1})
    def buy_labor(self):
        """ receives all labor offers and accepts them one by one """
        self.accept_offers("labor")
    def sell_goods(self):
        """ offers one unit of labor to firm 0, for the price of 1 "money" """
        self.sell('household', 0, good="GOOD", quantity=self.possession("GOOD"),
                  price=1)

@gui(parameters)
def main(parameters):
    w = Simulation(rounds=parameters['rounds'])
    w.declare_round_endowment(resource={'adult': 1}, product='labor')
    w.declare_perishable(good='labor')

    w.panel('household', possessions=['money', 'GOOD'],
                         variables=['current_utiliy'])
    w.panel('firm', possessions=['money', 'GOOD'])

    firms = w.build_agents(Firm, 'firm', 1)
    households = w.build_agents(Household, 'household', 1)
    for r in w.next_round():
        households.do('sell_labor')
        firms.do('buy_labor')
        # uses all labor that is available and produces
        # according to the set cobb_douglas function
        firms.do('produce_use_everything')
        firms.do('panel')
        firms.do('sell_goods')
        households.do('buy_goods')
        households.do('panel')
        households.do('consumption')

if __name__ == '__main__':
    main(parameters)
