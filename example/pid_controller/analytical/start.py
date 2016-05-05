""" A simulation of the first Model of Ernesto Carrella's paper:
Sticky Prices Microfoundations in a Agent Based Supply Chain
Section 4 Firms and Production

Here we have one firm and one market agent. The market agent
has the demand function q = 102 - p

"""
from __future__ import division
from multiprocessing import freeze_support
from firm import Firm
from market import Market
from abce import Simulation, gui



simulation_parameters = {'name': "analytical",
                         'random_seed': None,
                         'rounds': 3000}

@gui(simulation_parameters)
def main(simulation_parameters):
    s = Simulation(rounds=simulation_parameters['rounds'])
    action_list = [
        ('firm', 'my_production'),
        ('firm', 'selling'),
        ('market', 'buying'),
        ('firm', 'adjust_price'),
        ('firm', 'adjust_quantity'),
        ('market', 'consumption')
    ]

    s.add_action_list(action_list)

    s.build_agents(Firm, 'firm', parameters=simulation_parameters, number=1)
    s.build_agents(Market, 'market', parameters=simulation_parameters, number=1)

    s.run()

if __name__ == '__main__':
    main(simulation_parameters)
