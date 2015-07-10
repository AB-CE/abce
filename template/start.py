from __future__ import division
import multiprocessing as mp
from firm import Firm
from household import Household
from abce import Simulation, read_parameters, repeat

def main()
    for simulation_parameters in read_parameters('simulation_parameters.csv'):
        s = Simulation(simulation_parameters)
        action_list = [
        repeat([
            ('firm', 'one'),
            ('household', 'two'),
            ], simulation_parameters['trade_repetitions']),
            'buy_log',
            ('all', 'three')
        ]
        s.add_action_list(action_list)

        s.build_agents(Firm, 5)
        s.build_agents(Household, 5)

        s.declare_round_endowment(
                    resource='labor_endowment',
                    productivity=1,
                    product='labor'
        )
        s.declare_perishable(good='labor')

        s.panel_data('household', command='buy_log')
        s.panel_data('firm', command='buy_log')

        s.run()

if __name__ == '__main__':
    mp.freeze_support()
    main()

