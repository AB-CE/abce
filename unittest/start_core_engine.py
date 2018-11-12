from buy import Buy
from sell import Sell
from give import Give
from logger_test import LoggerTest
from abcEconomics import Simulation


def main(processes, rounds):
    s = Simulation(processes=processes, name='unittest')

    print('build Buy')
    buy = s.build_agents(Buy, 'buy', 1000, rounds=rounds)
    print('build Sell')
    sell = s.build_agents(Sell, 'sell', 1000, rounds=rounds)
    print('build Give')
    give = s.build_agents(Give, 'give', 2, rounds=rounds)
    print('build LoggerTest')
    loggertest = s.build_agents(
        LoggerTest, 'loggertest', 1, rounds=rounds)

    all = buy + sell + give + loggertest

    for r in range(rounds):
        s.advance_round(r)
        for _ in range(5):
            buy.one()
            buy.two()
            buy.three()
            buy.clean_up()
        buy.panel_log(variables=['price'])
        for _ in range(5):
            sell.one()
            sell.two()
            sell.three()
            sell.clean_up()
        for _ in range(5):
            give.one()
            give.two()
            give.three()
            give.clean_up()
        for _ in range(5):
            loggertest.one()
            loggertest.two()
            loggertest.three()
            loggertest.clean_up()

        all.all_tests_completed()
    s.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=3)
    print('Iteration with 1 core finished')
    main(processes=2, rounds=3)
    print('Iteration with multiple processes finished')
