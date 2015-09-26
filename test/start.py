from __future__ import division
import multiprocessing as mp
from firm import Firm
from household import Household
from abce import Simulation, read_parameters



def main():
    for simulation_parameters in read_parameters('simulation_parameters.csv'):
        s = Simulation(simulation_parameters)
        action_list = [
            repeat([
                       ('firm', 'selling', 'parallel'),
                       ('household', 'buying'),
                       ('household', 'checking')
                       ], 60)]
        s.add_action_list(action_list)

        s.declare_round_endowment('field', 60, 'corn')
        s.declare_round_endowment('shares', 60, 'money')

        s.build_agents(Firm, 1)
        s.build_agents(Household, 1)

        s.run()

if __name__ == '__main__':
    mp.freeze_support()
    main()
