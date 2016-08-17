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

parameters = {'name': '2x2',
              'random_seed': None,
              'rounds': 2500,
              'num_firms': 10}

#@gui(parameters)
def main(parameters):
    simulation = Simulation(rounds=parameters['rounds'], processes=1)
    action_list = [
        ('household', 'sell_labor'),
        ('firm', 'buy_labor'),
        ('firm', 'production'),
        ('firm', 'panel'),
        ('firm', 'quotes'),
        ('household', 'buy_goods'),
        ('firm', 'sell_goods'),
        ('household', 'aggregate'),
        ('household', 'consumption'),
        ('firm', 'adjust_price')]
    simulation.add_action_list(action_list)

    simulation.declare_round_endowment(resource='adult', units=1, product='labor')
    simulation.declare_perishable(good='labor')

    simulation.aggregate('household', possessions=['money', 'GOOD'],
                         variables=['current_utiliy'])
    simulation.panel('firm', possessions=['money', 'GOOD'],
                    variables=['price', 'inventory'])

    simulation.build_agents(Firm, 'firm', number=parameters['num_firms'])
    simulation.build_agents(Household, 'household', number=1, parameters=parameters)

    simulation.run()
    simulation.graphs()

if __name__ == '__main__':
    main(parameters)
