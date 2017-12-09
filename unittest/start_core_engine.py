from buy import Buy
# from quote_buy import QuoteBuy
from sell import Sell
from give import Give  # tests give and messaging
from logger_test import LoggerTest
from endowment import Endowment
from buyexpiringcapital import BuyExpiringCapital
from abce import Simulation
from messagea import MessageA
from messageb import MessageB


def main(processes, rounds):
    s = Simulation(processes=processes, name='unittest')
    s.declare_round_endowment(
        resource='labor_endowment', units=5, product='labor')
    s.declare_round_endowment(resource='cow', units=10,
                              product='milk')
    s.declare_perishable(good='labor')

    # s.declare_expiring('xcapital', 5)
    print('build Buy')
    buy = s.build_agents(Buy, 'buy', 1000, rounds=rounds)
    print('build Sell')
    # s.build_agents(QuoteBuy, 2)
    sell = s.build_agents(Sell, 'sell', 1000, rounds=rounds)
    print('build Give')
    give = s.build_agents(Give, 'give', 2, rounds=rounds)  # tests give and messaging
    print('build Endowment')
    endowment = s.build_agents(Endowment, 'endowment', 2, rounds=rounds, creation=0)
    # tests declare_round_endowment and declare_perishable
    print('build LoggerTest')
    loggertest = s.build_agents(
        LoggerTest, 'loggertest', 1, rounds=rounds)

    # print('build ContractSeller')
    # contractseller = s.build_agents(ContractSeller, 'contractseller', 2,
    #    rounds=rounds)
    # print('build ContractBuyer')
    # contractbuyer = s.build_agents(ContractBuyer, 'contractbuyer', 2,
    #    rounds=rounds)
    # print('build ContractSellerStop')
    # contractsellerstop = s.build_agents(ContractSellerStop,
    #    'contractsellerstop', 2, rounds=rounds)
    # print('build ContractBuyerStop')
    # contractbuyerstop = s.build_agents(ContractBuyerStop,
    #    'contractbuyerstop', 2, rounds=rounds)
    # s.build_agents(ExpiringCapital, 1)
    # s.build_agents(GiveExpiringCapital, 2)
    print('build BuyExpiringCapital')
    _ = s.build_agents(BuyExpiringCapital, 'buyexpiringcapital', 2,
                       rounds=rounds)
    print('build MessageA')
    messagea = s.build_agents(MessageA, 'messagea', 20)
    print('build MessageB')
    messageb = s.build_agents(MessageB, 'messageb', 20)

    some = buy + sell + give + loggertest
#    contractagents = (contractbuyer + contractseller
#                      + contractbuyerstop + contractsellerstop)

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
        (messagea + messageb).sendmsg()
        (messageb + messagea).recvmsg()
        endowment.Iconsume()
        # (contractbuyer + contractbuyerstop).request_offer()
        # (contractseller + contractsellerstop).make_offer()
        # contractagents.accept_offer()
        # contractagents.deliver()
        # contractagents.pay()
        # contractagents.control()

        some.all_tests_completed()
    s.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=5)
    print('Iteration with 1 core finished')
    main(processes=4, rounds=5)
    print('Iteration with multiple processes finished')
