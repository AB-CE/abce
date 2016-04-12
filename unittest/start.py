from __future__ import division
from buy import Buy
#from quote_buy import QuoteBuy
from sell import Sell
from give import Give  # tests give and messaging
from logger_test import LoggerTest
from endowment import Endowment
from production_multifirm import ProductionMultifirm
from production_firm import ProductionFirm
from utility_household import UtilityHousehold
from contractseller import ContractSeller
from contractbuyer import ContractBuyer
from expiringcapital import ExpiringCapital
from giveexpiringcapital import GiveExpiringCapital
from buyexpiringcapital import BuyExpiringCapital
from abce import Simulation, read_parameters, repeat


def main():
    all = ['buy',
           'sell',
           'give',
           'endowment',
           'loggertest',
           'productionmultifirm',
           'productionfirm',
           'utilityhousehold']

    for parameters in read_parameters('simulation_parameters.csv'):
        s = Simulation(parameters)
        action_list = [
            repeat([
                (all, 'one'),
                (all, 'two'),
                (all, 'three'),
                (all, 'clean_up')
                ], 20),
            #('buy', 'panel'),
            ('endowment', 'Iconsume'),
            ('productionmultifirm', 'production'),
            ('productionfirm', 'production'),
            ('utilityhousehold', 'consumption'),

            #('contractseller', 'make_offer'),
            #('contractseller', 'accept_offer'),
            #('contractseller', 'deliver_or_pay'),
            #('contractseller', 'control'),

            #('contractbuyer', 'request_offer'),
            #('contractbuyer', 'accept_offer'),
            #('contractbuyer', 'deliver_or_pay'),
            #('contractbuyer', 'control'),
            #('expiringcapital', 'go'),

            (all, 'all_tests_completed')]
        s.add_action_list(action_list)

        s.declare_round_endowment(resource='labor_endowment', units=5, product='labor')
        s.declare_round_endowment(resource='cow', units=10, product='milk')
        s.declare_perishable(good='labor')
        #s.panel('buy', variables=['price'])
        #s.declare_expiring('xcapital', 5)

        s.build_agents(Buy, 1000)
        #s.build_agents(QuoteBuy, 2)
        s.build_agents(Sell, 1000)
        s.build_agents(Give, 2)  # tests give and messaging
        s.build_agents(Endowment, 2)  # tests declare_round_endowment and declare_perishable
        s.build_agents(LoggerTest, 1)
        s.build_agents(ProductionMultifirm, 1)
        s.build_agents(ProductionFirm, 5)
        s.build_agents(UtilityHousehold, 5)
        #s.build_agents(ContractSeller, 2)
        #s.build_agents(ContractBuyer, 2)
        #s.build_agents(ExpiringCapital, 1)
        #s.build_agents(GiveExpiringCapital, 2)
        s.build_agents(BuyExpiringCapital, 2)

        s.run(parallel=True)

if __name__ == '__main__':
    main()
