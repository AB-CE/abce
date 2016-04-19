""" Agents are now build according
to the line in agents_parameter.csv
"""
from __future__ import division
import multiprocessing as mp
from abce import Simulation, gui
from firm import Firm
from household import Household


simulation_parameters = {'name': 'name',
                         'trade_logging': 'off',
                         'random_seed': None,
                         'rounds': 40}

@gui(simulation_parameters)
def main(simulation_parameters):
    w = Simulation(rounds=simulation_parameters['rounds'])
    action_list = [
    ('household', 'sell_labor'),
    ('firm', 'buy_inputs'),
    ('firm', 'production'),
    ('firm', 'panel'),
    ('firm', 'sell_intermediary_goods'),
    ('household', 'buy_intermediary_goods'),
    ('household', 'panel'),
    ('household', 'consumption')
    ]
    w.add_action_list(action_list)

    w.declare_round_endowment(resource='labor_endowment', units=5, product='labor')
    w.declare_perishable(good='labor')

    w.panel('household')
    w.panel('firm')

    w.build_agents(Firm, 2)
    w.build_agents(Household, 2)

    w.run()
    #w.graphs()

if __name__ == '__main__':
    main(simulation_parameters)
