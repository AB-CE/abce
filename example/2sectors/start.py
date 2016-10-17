""" Agents are now build according
to the line in agents_parameter.csv
"""
from __future__ import division
from abce import Simulation, gui
from firm import Firm
from household import Household


simulation_parameters = {'name': 'name',
                         'trade_logging': 'off',
                         'random_seed': None,
                         'rounds': 40}

#@gui(simulation_parameters)
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

    w.panel('household', possessions=['consumption_good'])
    w.panel('firm', possessions=['consumption_good', 'intermediate_good'])

    w.build_agents(Firm, 'firm', 2)
    w.build_agents(Household, 'household', 2)

    w.run()


if __name__ == '__main__':
    main(simulation_parameters)
