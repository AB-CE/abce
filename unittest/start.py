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
from contractsellerstop import ContractSellerStop
from contractbuyerstop import ContractBuyerStop
from expiringcapital import ExpiringCapital
from giveexpiringcapital import GiveExpiringCapital
from buyexpiringcapital import BuyExpiringCapital
from abce import Simulation, repeat
from messagea import MessageA
from messageb import MessageB
from addagent import AddAgent

def main():
    rounds = 30
    all = ['buy',
           'sell',
           'give',
           'endowment',
           'loggertest',
           'productionmultifirm',
           'productionfirm',
           'utilityhousehold']

    contractagents = ['contractbuyer', 'contractseller',
                      'contractbuyerstop', 'contractsellerstop']

    s = Simulation(rounds=rounds, cores=None)
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
        (('messagea', 'messageb'), 'sendmsg'),
        (('messageb', 'messagea'), 'recvmsg'),

        (('contractbuyer','contractbuyerstop'), 'request_offer'),
        (('contractseller', 'contractsellerstop'), 'make_offer'),
        (contractagents, 'accept_offer'),
        (contractagents, 'deliver'),
        (contractagents, 'pay'),
        (contractagents, 'control'),

        #('expiringcapital', 'go'),

        (all, 'all_tests_completed'),
        ('addagent', 'add_agent')]
    s.add_action_list(action_list)

    s.declare_round_endowment(resource='labor_endowment', units=5, product='labor')
    s.declare_round_endowment(resource='cow', units=10, product='milk')
    s.declare_perishable(good='labor')
    #s.panel('buy', variables=['price'])
    #s.declare_expiring('xcapital', 5)

    s.build_agents(Buy, 'buy', 1000, parameters={'rounds': rounds})
    #s.build_agents(QuoteBuy, 2)
    s.build_agents(Sell, 'sell', 1000, parameters={'rounds': rounds})
    s.build_agents(Give, 'give', 2, parameters={'rounds': rounds}, expandable=True) # tests give and messaging
    s.build_agents(Endowment, 'endowment', 2, parameters={'rounds': rounds}, expandable=True)  # tests declare_round_endowment and declare_perishable
    s.build_agents(LoggerTest, 'loggertest', 1, parameters={'rounds': rounds})
    s.build_agents(ProductionMultifirm, 'productionmultifirm', 1, parameters={'rounds': rounds})
    s.build_agents(ProductionFirm, 'productionfirm', 5, parameters={'rounds': rounds})
    s.build_agents(UtilityHousehold, 'utilityhousehold', 5, parameters={'rounds': rounds})
    s.build_agents(ContractSeller, 'contractseller', 2, parameters={'rounds': rounds})
    s.build_agents(ContractBuyer, 'contractbuyer', 2, parameters={'rounds': rounds})
    s.build_agents(ContractSellerStop, 'contractsellerstop', 2, parameters={'rounds': rounds})
    s.build_agents(ContractBuyerStop, 'contractbuyerstop', 2, parameters={'rounds': rounds})
    #s.build_agents(ExpiringCapital, 1)
    #s.build_agents(GiveExpiringCapital, 2)
    s.build_agents(BuyExpiringCapital, 'buyexpiringcapital', 2, parameters={'rounds': rounds})
    s.build_agents(MessageA, 'messagea', 20, parameters={'rounds': rounds}, expandable=True)
    s.build_agents(MessageB, 'messageb', 20, parameters={'rounds': rounds}, expandable=True)
    s.build_agents(AddAgent, 'addagent', 1, parameters={'rounds': rounds})

    s.run()

if __name__ == '__main__':
    main()
