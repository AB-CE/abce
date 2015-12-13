""" Agents are now build according
to the line in agents_parameter.csv
"""
from __future__ import division
import multiprocessing as mp
from abce import Simulation, read_parameters
from firm import Firm
from household import Household


def main():
    simulation_parameters = {'name': 'name',
    'trade_logging': 'off',

    }
    w = Simulation(simulation_parameters)
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

    w.build_agents_from_file(Firm, parameters_file='agent_parameters.csv')
    w.build_agents_from_file(Household, parameters_file='agent_parameters.csv')

    w.run()

if __name__ == '__main__':
    main()
