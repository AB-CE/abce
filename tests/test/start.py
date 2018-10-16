from __future__ import division
import multiprocessing as mp
from firm import Firm
from household import Household
from abcEconomics import Simulation

simulation_parameters = {'name': 'test_sim_1_',
                         'random_seed': None,
                         'num_rounds': 30,
                         'trade_logging': 'individual',
                         'trade_repetitions': 10}


def main():
    for params in simulation_parameters:
        s = Simulation(params)

        s.declare_round_endowment('field', 60, 'corn')
        s.declare_round_endowment('shares', 60, 'money')

        f = s.build_agents(Firm, 'firm', 1)
        h = s.build_agents(Household, 'household', 1)
        for r in s.next_round():
            for i in range(60):
                f.do('selling')
                h.do('buying')
                h.do('checking')

        s.run()


if __name__ == '__main__':
    mp.freeze_support()
    main()
