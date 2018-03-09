import abce
from buy import Buy


def main(processes, rounds=20):
    s = abce.Simulation(processes=processes, name='unittest')
    s.declare_round_endowment(
        resource='labor_endowment', units=5, product='labor')
    s.declare_round_endowment(resource='cow', units=10,
                              product='milk')
    s.declare_perishable(good='labor')

    print('build Buy')
    buy = s.build_agents(Buy, 'buy', 1000, rounds=rounds)

    for r in range(rounds):
        s.advance_round(r)
        for _ in range(5):
            buy.one()
            buy.two()
            buy.three()
            buy.clean_up()
        buy.panel_log(variables=['price'])
        buy.all_tests_completed()
    s.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=5)
    print('Iteration with 1 core finished')
    main(processes=4, rounds=5)
    print('Iteration with multiple processes finished')
