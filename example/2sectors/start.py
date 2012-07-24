""" Agents are now build according
to the line in agents_parameter.csv
"""

from __future__ import division
import sys
sys.path.append('../../lib')  # <--------- modify this to your abce/lib path
from abce import *
from firm import Firm
from household import Household


for parameters in read_parameters('simulation_parameters.csv'):
    w = Simulation(parameters)
    action_list = [
    ('household', 'sell_labor'),
    ('firm', 'buy_inputs'),
    ('firm', 'production'),
    'production_log',

    ('firm', 'sell_intermediary_goods'),
    ('household', 'buy_intermediary_goods'),
    'buy_log',
    ('household', 'consumption')
    ]
    w.add_action_list(action_list)

    w.build_agents_from_file(Firm)
    w.build_agents_from_file(Household)

    w.declare_round_endowment('labor_endowment', productivity=1, product='labor')
    w.declare_perishable(good='labor')

    w.panel_data('household', command='buy_log')
    w.panel_data('firm', command='production_log')

    w.run()

