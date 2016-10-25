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
              'rounds': 10}

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
        firms.do('production')
        firms.do('panel')
        firms.do('sell_goods')
        households.do('buy_goods')
        households.do('panel')
        households.do('consumption')

if __name__ == '__main__':
    main(parameters)
