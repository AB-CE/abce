from __future__ import division
import sys
sys.path.append('../lib')
from buy import Buy
from sell import Sell
from give import Give  # tests give and messaging
from endowment import Endowment
from abce import *


for parameters in read_parameters('simulation_parameters.csv'):
    s = Simulation(parameters)
    action_list = [
        repeat([
        ('all', 'one'),
        ('all', 'two'),
        ('all', 'three'),
        ('all', 'clean_up')
        ], 1000),
        ('endowment', 'Iconsume'),
        ('all', 'all_tests_completed')

    ]
    s.add_action_list(action_list)

    s.build_agents(Buy, 2)
    s.build_agents(Sell, 2)
    s.build_agents(Give, 2)  # tests give and messaging
    s.build_agents(Endowment, 2)  # tests declare_round_endowment and declare_perishable

    s.declare_round_endowment(resource='labor_endowment', productivity=5, product='labor')
    s.declare_round_endowment(resource='cow', productivity=10, product='milk')
    s.declare_perishable(good='labor')

    # s.panel_data('Firm', command='buy_log')

    s.run()

