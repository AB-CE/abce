""" 1. declared the timeline
    2. build one Household and one Firm follow_agent
    3. For every labor_endowment an agent has he gets one trade or usable labor
    per round. If it is not used at the end of the round it disapears.
    4. Firms' and Households' possesions are monitored ot the points marked in
    timeline.
"""

from __future__ import division
import sys
sys.path.append('../../lib')
from abce import *
from firm import Firm
from household import Household


for parameters in read_parameters():
    w = Simulation(parameters)
    action_list = [
    ('household', 'sell_labor'),
    ('firm', 'buy_labor'),
    ('firm', 'production'),
    'production_log',
    ('firm', 'sell_intermediary_goods'),
    ('household', 'buy_intermediary_goods'),
    'buy_log',
    ('household', 'consumption')
    ]
    w.add_action_list(action_list)

    w.build_agents(Firm, 1)
    w.build_agents(Household, 1)

    w.declare_round_endowment(resource='labor_endowment', productivity=1, product='labor')
    w.declare_perishable(good='labor')

    w.panel_data('household', command='buy_log')
    w.panel_data('firm', command='production_log')

    w.run()

