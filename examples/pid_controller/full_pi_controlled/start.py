""" A simulation of the first Model of Ernesto Carrella's paper:
Sticky Prices Microfoundations in a Agent Based Supply Chain
Section 4 Firms and Production

Here we have one firm and one market agent. The market agent
has the demand function q = 102 - p

"""
from __future__ import division
from firm import Firm
from market import Market
from labormarket import LaborMarket
from abce import Simulation, gui

simulation_parameters = {
    'name': 'Sticky Prices Microfoundations', 'rounds': 20}


@gui(simulation_parameters)
def main(simulation_parameters):
    s = Simulation(**simulation_parameters)
    s.declare_perishable('labor')

    firms = s.build_agents(Firm, 'firm', 1)
    market = s.build_agents(Market, 'market', 1)
    labormarket = s.build_agents(LaborMarket, 'labormarket', 1)
    for r in s.next_round():
        firms.do('quote_hire')
        labormarket.do('accepting')
        firms.do('hire')
        firms.do('my_production')
        firms.do('selling')
        market.do('buying')
        firms.do('adjust_price')
        firms.do('adjust_quantity')
        market.do('consumption')


if __name__ == '__main__':
    main(simulation_parameters)
