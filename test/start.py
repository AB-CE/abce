from __future__ import division
import multiprocessing as mp
from firm import Firm
from household import Household
from abce import Simulation, repeat

simulation_parameters = [
        {'name': 'test_sim_1_',
         'random_seed': None,
         'rounds': 30,
         'trade_logging': 'individual',
         'trade_repetitions': 10
         }]

def main():
    for params in simulation_parameters:
        s = Simulation(params)
        action_list = [
            repeat([
                       ('firm', 'selling', 'parallel'),
                       ('household', 'buying'),
                       ('household', 'checking')
                       ], 60)]
        s.add_action_list(action_list)

        s.declare_round_endowment('field', 60, 'corn')
        s.declare_round_endowment('shares', 60, 'money')

        s.build_agents(Firm, 'firm', 1)
        s.build_agents(Household, 'firm', 1)

        s.run()

if __name__ == '__main__':
    mp.freeze_support()
    main()
