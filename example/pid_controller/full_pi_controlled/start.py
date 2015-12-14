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
import graphs

simulation_parameters = {'name': 'Sticky Prices Microfoundations'}

@gui(simulation_parameters)
def main(simulation_parameters):
    s = Simulation(simulation_parameters)
    action_list = [
        ('firm', 'quote_hire'),
        ('labormarket', 'accepting'),
        ('firm', 'hire'),
        ('firm', 'my_production'),
        ('firm', 'selling'),
        ('market', 'buying'),
        ('firm', 'adjust_price'),
        ('firm', 'adjust_quantity'),
        ('market', 'consumption')
    ]

    s.add_action_list(action_list)
    s.declare_perishable('labor')

    s.build_agents(Firm, 1)
    s.build_agents(Market, 1)
    s.build_agents(LaborMarket, 1)

    s.run()

if __name__ == '__main__':
    main(simulation_parameters)
