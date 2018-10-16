from __future__ import division
from buy import Buy
from sell import Sell
from abcEconomics import Simulation

simulation_parameters = {'name': 'round',
                         'random_seed': None,
                         'num_rounds': 30,
                         'trade_logging': 'individual',
                         'cut_of': 0.00000001}


def main():
    s = Simulation()
    buy = s.build_agents(Buy, group_name='buy', number=2,
                         parameters=simulation_parameters)
    sell = s.build_agents(Sell, group_name='sell', number=2,
                          parameters=simulation_parameters)

    all = buy + sell

    for r in range(simulation_parameters['num_rounds']):
        s.advance_round(r)
        for r in range(20000):
            all.one()
            all.two()
            all.three()
            all.clean_up()

        all.all_tests_completed()


if __name__ == '__main__':
    main()
