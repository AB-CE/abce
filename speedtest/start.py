from __future__ import division
from buy import Buy
from sell import Sell
from abce import Simulation, read_parameters, repeat


def main():
    all = ['buy',
           'sell']

    for parameters in read_parameters('simulation_parameters.csv'):
        s = Simulation(parameters)
        action_list = [
            repeat([
                (all, 'one'),
                (all, 'two'),
                (all, 'three'),
                (all, 'clean_up')
                ], 20000),

            ('all', 'all_tests_completed')]
        s.add_action_list(action_list)

        s.declare_round_endowment(resource='labor_endowment', units=5, product='labor')
        s.declare_round_endowment(resource='cow', units=10, product='milk')
        s.declare_perishable(good='labor')
        #s.panel('buy', variables=['price'])
        #s.declare_expiring('xcapital', 5)

        s.build_agents(Buy, 2)
        s.build_agents(Sell, 2)

        s.run()

if __name__ == '__main__':
    main()
