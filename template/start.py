from __future__ import division
import sys
sys.path.append('../abce/lib')
from firm import Firm
from household import Household
from abce import *


for parameters in read_parameters('simulation_parameters.csv'):
    s = Simulation(parameters)
    action_list = [
    repeat([
        ('Firm', 'one'),
        ('Household', 'two'),
        repetitions=10)
        'buy_log'
        ('all', 'three')]
    ]
    s.add_action_list(action_list)

    s.build_agents(Firm, 5)
    s.build_agents(Household, 5)

    s.declare_round_endowment(resource='labor_endowment', productivity=1, product='labor')
    s.declare_perishable(good='labor')

    s.panel_data('Household', command='buy_log')
    s.panel_data('Firm', command='buy_log')

    s.run()

