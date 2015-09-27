""" 1. declared the timeline
    2. build one Household and one Firm follow_agent
    3. For every labor_endowment an agent has he gets one trade or usable labor
    per round. If it is not used at the end of the round it disapears.
    4. Firms' and Households' possesions are monitored ot the points marked in
    timeline.
"""

from __future__ import division
import multiprocessing as mp
from abce import Simulation, read_parameters
from firm import Firm
from household import Household


def main():
    for parameters in read_parameters():
        w = Simulation(parameters)
        action_list = [
            ('household', 'sell_labor'),
            ('firm', 'buy_labor'),
            ('firm', 'production'),
            ('firm', 'panel'),
            ('firm', 'sell_goods'),
            ('household', 'buy_goods'),
            ('household', 'panel'),
            ('household', 'consumption')
        ]
        w.add_action_list(action_list)

        w.declare_round_endowment(resource='adult', units=1, product='labor')
        w.declare_perishable(good='labor')

        w.panel('household')
        w.panel('firm')

        w.build_agents(Firm, 1)
        w.build_agents(Household, 1)

        w.run()

if __name__ == '__main__':
    mp.freeze_support()
    main()
