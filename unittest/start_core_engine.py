from __future__ import division
from __future__ import print_function
from buy import Buy
# from quote_buy import QuoteBuy
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
from abce import Simulation
from messagea import MessageA
from messageb import MessageB
from addagent import AddAgent
from killer import Killer
from victim import Victim


def main(processes, rounds):
    s = Simulation(processes=processes, name='unittest')
    s.declare_round_endowment(
        resource='labor_endowment', units=5, product='labor', groups=['all'])
    s.declare_round_endowment(resource='cow', units=10,
                              product='milk', groups=['all'])
    s.declare_perishable(good='labor')
    s.panel('Buy', variables=['price'])
    # s.declare_expiring('xcapital', 5)
    print('build Buy')
    buy = s.build_agents(Buy, 1000, parameters={'rounds': rounds})
    print('build Sell')
    # s.build_agents(QuoteBuy, 2)
    sell = s.build_agents(Sell, 1000, parameters={'rounds': rounds})
    print('build Give')
    give = s.build_agents(Give, 2, parameters={
                          'rounds': rounds})  # tests give and messaging
    print('build Endowment')
    endowment = s.build_agents(Endowment, 2, parameters={
                               'rounds': rounds, 'creation': 0})
    # tests declare_round_endowment and declare_perishable
    print('build LoggerTest')
    loggertest = s.build_agents(
        LoggerTest, 1, parameters={'rounds': rounds})
    print('build ProductionMultifirm')
    productionmultifirm = s.build_agents(
        ProductionMultifirm, 1,
        parameters={'rounds': rounds})
    print('build ProductionFirm')
    productionfirm = s.build_agents(
        ProductionFirm, 7, parameters={'rounds': rounds})
    print('build UtilityHousehold')
    utilityhousehold = s.build_agents(
        UtilityHousehold, 5,
        parameters={'rounds': rounds})
    # print('build ContractSeller')
    # contractseller = s.build_agents(ContractSeller, 2,
    #    parameters={'rounds': rounds})
    # print('build ContractBuyer')
    # contractbuyer = s.build_agents(ContractBuyer, 2,
    #    parameters={'rounds': rounds})
    # print('build ContractSellerStop')
    # contractsellerstop = s.build_agents(ContractSellerStop,
    #    2, parameters={'rounds': rounds})
    # print('build ContractBuyerStop')
    # contractbuyerstop = s.build_agents(ContractBuyerStop,
    #    2, parameters={'rounds': rounds})
    # s.build_agents(ExpiringCapital, 1)
    # s.build_agents(GiveExpiringCapital, 2)
    print('build BuyExpiringCapital')
    _ = s.build_agents(BuyExpiringCapital, 2,
                       parameters={'rounds': rounds})
    print('build MessageA')
    messagea = s.build_agents(MessageA,
                              20, parameters={'rounds': rounds})
    print('build MessageB')
    messageb = s.build_agents(MessageB,
                              20, parameters={'rounds': rounds})
    print('build Killer')
    killer = s.build_agents(Killer, 1,
                            parameters={'rounds': rounds})
    print('build Victim')
    victim = s.build_agents(Victim, rounds,
                            parameters={'rounds': rounds})
    print('build Victim loudvictim')
    _ = s.build_agents(
        Victim, rounds, group_name='Loudvictim', parameters={'rounds': rounds})

    some = buy + sell + give + loggertest + utilityhousehold

#    contractagents = (contractbuyer + contractseller
#                      + contractbuyerstop + contractsellerstop)

    print('build AddAgent')
    addagent = s.build_agents(AddAgent, 0)
    for r in range(rounds):
        s.advance_round(r)
        for _ in range(5):
            buy.do('one')
            buy.do('two')
            buy.do('three')
            buy.do('clean_up')
        buy.do('panel')
        for _ in range(5):
            sell.do('one')
            sell.do('two')
            sell.do('three')
            sell.do('clean_up')
        for _ in range(5):
            give.do('one')
            give.do('two')
            give.do('three')
            give.do('clean_up')
        for _ in range(5):
            loggertest.do('one')
            loggertest.do('two')
            loggertest.do('three')
            loggertest.do('clean_up')
        for _ in range(5):
            utilityhousehold.do('one')
            utilityhousehold.do('two')
            utilityhousehold.do('three')
            utilityhousehold.do('clean_up')
        endowment.do('Iconsume')
        productionmultifirm.do('production')
        productionfirm.do('production')
        utilityhousehold.do('consumption')
        (messagea + messageb).do('sendmsg')
        (messageb + messagea).do('recvmsg')
        # (contractbuyer + contractbuyerstop).do('request_offer')
        # (contractseller + contractsellerstop).do('make_offer')
        # contractagents.do('accept_offer')
        # contractagents.do('deliver')
        # contractagents.do('pay')
        # contractagents.do('control')
        killer.do('kill')
        killer.do('send_message')
        victim.do('am_I_dead')
        some.do('all_tests_completed')
        addagent.do('add_agent')
    s.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=5)
    print('Iteration with 1 core finished')
    main(processes=4, rounds=5)
    print('Iteration with multiple processes finished')
