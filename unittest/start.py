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
from killer import Killer
from victim import Victim


def main(processes, rounds):
    all = ['buy',
           'sell',
           'give',
           'loggertest',
           'utilityhousehold']

    contractagents = ['contractbuyer', 'contractseller',
                      'contractbuyerstop', 'contractsellerstop']

    s = Simulation(rounds=rounds, processes=processes)
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
        ('killer', 'kill'),
        ('killer', 'send_message'),
        ('victim', 'am_I_dead'),

        #('expiringcapital', 'go'),

        (all, 'all_tests_completed'),
        ('addagent', 'add_agent')]
    s.add_action_list(action_list)

    s.declare_round_endowment(resource='labor_endowment', units=5, product='labor')
    s.declare_round_endowment(resource='cow', units=10, product='milk')
    s.declare_perishable(good='labor')
    #s.panel('buy', variables=['price'])
    #s.declare_expiring('xcapital', 5)
    print 'build Buy'
    s.build_agents(Buy, 'buy', 1000, parameters={'rounds': rounds})
    print 'build Sell'
    #s.build_agents(QuoteBuy, 2)
    s.build_agents(Sell, 'sell', 1000, parameters={'rounds': rounds})
    print 'build Give'
    s.build_agents(Give, 'give', 2, parameters={'rounds': rounds}) # tests give and messaging
    print 'build Endowment'
    s.build_agents(Endowment, 'endowment', 2, parameters={'rounds': rounds, 'creation': 0})  # tests declare_round_endowment and declare_perishable
    print 'build LoggerTest'
    s.build_agents(LoggerTest, 'loggertest', 1, parameters={'rounds': rounds})
    print 'build ProductionMultifirm'
    s.build_agents(ProductionMultifirm, 'productionmultifirm', 1, parameters={'rounds': rounds})
    print 'build ProductionFirm'
    s.build_agents(ProductionFirm, 'productionfirm', 7, parameters={'rounds': rounds})
    print 'UtilityHousehold'
    s.build_agents(UtilityHousehold, 'utilityhousehold', 5, parameters={'rounds': rounds})
    print 'build ContractSeller'
    s.build_agents(ContractSeller, 'contractseller', 2, parameters={'rounds': rounds})
    print 'build ContractBuyer'
    s.build_agents(ContractBuyer, 'contractbuyer', 2, parameters={'rounds': rounds})
    print 'build ContractSellerStop'
    s.build_agents(ContractSellerStop, 'contractsellerstop', 2, parameters={'rounds': rounds})
    print 'build ContractBuyerStop'
    s.build_agents(ContractBuyerStop, 'contractbuyerstop', 2, parameters={'rounds': rounds})
    #s.build_agents(ExpiringCapital, 1)
    #s.build_agents(GiveExpiringCapital, 2)
    print 'build BuyExpiringCapital'
    s.build_agents(BuyExpiringCapital, 'buyexpiringcapital', 2, parameters={'rounds': rounds})
    print 'build MessageA'
    s.build_agents(MessageA, 'messagea', 20, parameters={'rounds': rounds})
    print 'build MessageB'
    s.build_agents(MessageB, 'messageb', 20, parameters={'rounds': rounds})
    print 'build AddAgent'
    s.build_agents(AddAgent, 'addagent', 1, parameters={'rounds': rounds})
    print 'build Killer'
    s.build_agents(Killer, 'killer', 1, parameters={'rounds': rounds})
    print 'build Victim'
    s.build_agents(Victim, 'victim', rounds, parameters={'rounds': rounds})
    print 'build Victim loudvictim'
    s.build_agents(Victim, 'loudvictim', rounds, parameters={'rounds': rounds})

    s.run()

if __name__ == '__main__':
    main(processes=1, rounds=10)
    print 'Iteration with 1 core finished'
    main(processes=None, rounds=20)
    print 'Iteration with multiple processes finished'
