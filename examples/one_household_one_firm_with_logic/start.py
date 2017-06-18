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
    simulation.declare_round_endowment(resource='adult', units=1, product='labor')
    simulation.declare_perishable(good='labor')

    simulation.aggregate('household', possessions=['money', 'GOOD'],
                         variables=['current_utiliy'])
    simulation.panel('firm', possessions=['money', 'GOOD'],
                    variables=['price', 'inventory'])

    firms = simulation.build_agents(Firm, 'firm', number=parameters['num_firms'])
    households = simulation.build_agents(Household, 'household', number=1, parameters=parameters)

    for r in simulation.next_round():
        households.do('sell_labor')
        firms.do('buy_labor')
        firms.do('production')
        firms.do('panel')
        firms.do('quotes')
        households.do('buy_goods')
        firms.do('sell_goods')
        households.do('aggregate')
        households.do('consumption')
        firms.do('adjust_price')

    simulation.graphs()

if __name__ == '__main__':
    main(parameters)
