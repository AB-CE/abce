import abcEconomics
from production_multifirm import ProductionMultifirm
from utility_household import UtilityHousehold


def main(processes, rounds=5):
    s = abcEconomics.Simulation(processes=processes, name='production_consumption_test')
    print('build ProductionMultifirm')
    productionmultifirm = s.build_agents(ProductionMultifirm, 'productionmultifirm', 1, rounds=rounds)
    print('build UtilityHousehold')
    utilityhousehold = s.build_agents(UtilityHousehold, 'utilityhousehold', 5, rounds=rounds)

    all_agents = utilityhousehold + productionmultifirm

    for r in range(rounds):
        s.advance_round(r)
        productionmultifirm.production()
        utilityhousehold.consumption()
        all_agents.all_tests_completed()
    s.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=5)
    print('Iteration with 1 core finished')
    main(processes=2, rounds=5)
    print('Iteration with multiple processes finished')
