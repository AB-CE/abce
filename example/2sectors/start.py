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
    w.declare_round_endowment(resource='labor_endowment', units=5, product='labor')
    w.declare_perishable(good='labor')
    w.panel('household', possessions=['consumption_good'])
    w.panel('firm', possessions=['consumption_good', 'intermediate_good'])

    firms = w.build_agents(Firm, 'firm', 2)
    households = w.build_agents(Household, 'household', 2)
    for r in w.next_round():
        # to access round, just get the value of w.round
        # to access its datetime version, use w._round # todo, better naming
        households.do('sell_labor')
        firms.do('buy_inputs')
        firms.do('production')
        firms.do('panel')
        firms.do('sell_intermediary_goods')
        households.do('buy_intermediary_goods')
        households.do('panel')
        households.do('consumption')


if __name__ == '__main__':
    main(simulation_parameters)
