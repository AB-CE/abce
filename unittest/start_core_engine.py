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
        resource='labor_endowment', units=5, product='labor')
    s.declare_round_endowment(resource='cow', units=10,
                              product='milk')
    s.declare_perishable(good='labor')

    # s.declare_expiring('xcapital', 5)
    print('build Buy')
    buy = s.build_agents(Buy, 'buy', 1000, parameters={'rounds': rounds})
    print('build Sell')
    # s.build_agents(QuoteBuy, 2)
    sell = s.build_agents(Sell, 'sell', 1000, parameters={'rounds': rounds})
    print('build Give')
    give = s.build_agents(Give, 'give', 2, parameters={
                          'rounds': rounds})  # tests give and messaging
    print('build Endowment')
    endowment = s.build_agents(Endowment, 'endowment', 2, parameters={
                               'rounds': rounds, 'creation': 0})
    # tests declare_round_endowment and declare_perishable
    print('build LoggerTest')
    loggertest = s.build_agents(
        LoggerTest, 'loggertest', 1, parameters={'rounds': rounds})
    print('build ProductionMultifirm')
    productionmultifirm = s.build_agents(
        ProductionMultifirm, 'productionmultifirm', 1,
        parameters={'rounds': rounds})
    print('build ProductionFirm')
    productionfirm = s.build_agents(
        ProductionFirm, 'productionfirm', 7, parameters={'rounds': rounds})
    print('build UtilityHousehold')
    utilityhousehold = s.build_agents(
        UtilityHousehold, 'utilityhousehold', 5,
        parameters={'rounds': rounds})
    # print('build ContractSeller')
    # contractseller = s.build_agents(ContractSeller, 'contractseller', 2,
    #    parameters={'rounds': rounds})
    # print('build ContractBuyer')
    # contractbuyer = s.build_agents(ContractBuyer, 'contractbuyer', 2,
    #    parameters={'rounds': rounds})
    # print('build ContractSellerStop')
    # contractsellerstop = s.build_agents(ContractSellerStop,
    #    'contractsellerstop', 2, parameters={'rounds': rounds})
    # print('build ContractBuyerStop')
    # contractbuyerstop = s.build_agents(ContractBuyerStop,
    #    'contractbuyerstop', 2, parameters={'rounds': rounds})
    # s.build_agents(ExpiringCapital, 1)
    # s.build_agents(GiveExpiringCapital, 2)
    print('build BuyExpiringCapital')
    _ = s.build_agents(BuyExpiringCapital, 'buyexpiringcapital', 2,
                       parameters={'rounds': rounds})
    print('build MessageA')
    messagea = s.build_agents(MessageA, 'messagea',
                              20, parameters={'rounds': rounds})
    print('build MessageB')
    messageb = s.build_agents(MessageB, 'messageb',
                              20, parameters={'rounds': rounds})
    print('build Killer')
    killer = s.build_agents(Killer, 'killer', 1,
                            parameters={'rounds': rounds})
    print('build Victim')
    victim = s.build_agents(Victim, 'victim', rounds,
                            parameters={'rounds': rounds})
    print('build Victim loudvictim')
    _ = s.build_agents(
        Victim, 'loudvictim', rounds, parameters={'rounds': rounds})

    some = buy + sell + give + loggertest + utilityhousehold

#    contractagents = (contractbuyer + contractseller
#                      + contractbuyerstop + contractsellerstop)

    print('build AddAgent')
    addagent = s.build_agents(AddAgent, 'addagent', 0)
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
        for _ in range(5):
            utilityhousehold.one()
            utilityhousehold.two()
            utilityhousehold.three()
            utilityhousehold.clean_up()
        endowment.Iconsume()
        productionmultifirm.production()
        productionfirm.production()
        utilityhousehold.consumption()
        (messagea + messageb).sendmsg()
        (messageb + messagea).recvmsg()
        # (contractbuyer + contractbuyerstop).request_offer()
        # (contractseller + contractsellerstop).make_offer()
        # contractagents.accept_offer()
        # contractagents.deliver()
        # contractagents.pay()
        # contractagents.control()
        killer.kill()
        killer.send_message()
        victim.am_I_dead()
        some.all_tests_completed()
        addagent.add_agent()
    s.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=5)
    print('Iteration with 1 core finished')
    main(processes=4, rounds=5)
    print('Iteration with multiple processes finished')
