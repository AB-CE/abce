
from __future__ import division
from __future__ import print_function
from builtins import range
from abce import Simulation, gui
import abce


simulation_parameters = {'name': 'name',
                         'trade_logging': 'off',
                         'random_seed': None,
                         'rounds': 40}

class Household(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        """ self.employer is the _number_ of the agent that receives his
        labor offer.
        """
        self.create('labor_endowment', 1)
        self.set_cobb_douglas_utility_function({"consumption_good": 1})
        self.accumulated_utility = 0
        self.employer = self.id

    def sell_labor(self):
        """ offers one unit of labor to firm self.employer, for the price of 1 "money" """
        if self.employer % 2 == 0:
            self.sell('uFirm', 0, "labor", quantity=1, price=1)
        else:
            self.sell('dFirm', 0, "labor", quantity=1, price=1)

    def buy_consumption_goods(self):
        """ recieves the offers and accepts them one by one """
        for offer in self.get_offers("consumption_good"):
            self.accept(offer)

    def consumption(self):
        """ consumes_everything and logs the aggregate utility. current_utiliy
        """
        current_utiliy = self.consume_everything()
        self.accumulated_utility += current_utiliy
        self.log('HH', {'': self.accumulated_utility})

class downstreamFirm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        """downstream uses labor and the intermediary good to produce the final good"""
        self.create('money', 1)
        self.create('intermediate_good', 1)
        self.price = {'consumption_good': 1}
        self.inputs = {"labor": 1, "intermediate_good": 1}
        self.set_cobb_douglas({'consumption_good': 2}, self.inputs)
    def buy_inputs(self):
        for offer in self.get_offers("labor"):
            self.accept(offer)
        for offer in self.get_offers('intermediate_good'):
            self.accept(offer)
    def production(self):
        self.produce(self.inputs)
    def sell_goods(self):
        for i in range(2):
            self.sell('household', i, 'consumption_good', 1, 1)

class upstreamFirm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        """upstream produces an intermediary good
        there is an initial endowment to avoid bootstrapping problems
        """
        self.create('money', 2)
        self.price = {'intermediate_good': 1}
        self.inputs = {"labor": 1}
        self.set_cobb_douglas({'intermediate_good': 1}, self.inputs)
    def buy_inputs(self):
        for offer in self.get_offers("labor"):
            self.accept(offer)
    def production(self):
        self.produce(self.inputs)
    def sell_goods(self):
        self.sell('dFirm', 0, "intermediate_good", 1, 1)

#@gui(simulation_parameters)
def main(simulation_parameters):
    w = Simulation(rounds=simulation_parameters['rounds'])
    w.declare_round_endowment(resource={'labor_endowment': 5}, product='labor')
    w.declare_perishable(good='labor')
    w.panel('household', possessions=['consumption_good'])
    w.panel('uFirm', possessions=['consumption_good', 'intermediate_good'])
    w.panel('dFirm', possessions=['consumption_good', 'intermediate_good'])

    dFirms = w.build_agents(downstreamFirm, 'dFirm', 1)
    uFirms = w.build_agents(upstreamFirm, 'uFirm', 1)
    households = w.build_agents(Household, 'household', 2)
    for r in w.next_round():
        # to access round, just get the value of w.round
        # to access its datetime version, use w._round # todo, better naming
        households.do('sell_labor')
        (uFirms+dFirms).do('buy_inputs')
        (uFirms+dFirms).do('production')
        (uFirms+dFirms).do('panel')
        (uFirms+dFirms).do('sell_goods')
        households.do('buy_consumption_goods')
        households.do('panel')
        households.do('consumption')


if __name__ == '__main__':
    main(simulation_parameters)
