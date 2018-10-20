import logging

import abcEconomics
import platform


class MyAgent(abcEconomics.Agent):
    def init(self, agent_parameters):
        logging.debug('init', agent_parameters)
        self.mine = agent_parameters
        self.diff = False

    def call_me_maybe(self):
        logging.debug(self.name, self.mine)


class DifferentAgent(abcEconomics.Agent):
    def init(self, agent_parameters):
        logging.debug('init', agent_parameters)
        self.mine = agent_parameters
        self.diff = True

    def call_me_maybe(self):
        logging.debug('I am different', self.name, self.mine)


def main(processes, rounds):
    sim = abcEconomics.Simulation()

    myagent = sim.build_agents(MyAgent, 'myagent',
                               agent_parameters=[{'agent_parameters': 0},
                                                 {'agent_parameters': 1},
                                                 {'agent_parameters': 2},
                                                 {'agent_parameters': 3},
                                                 {'agent_parameters': 4},
                                                 {'agent_parameters': 5},
                                                 {'agent_parameters': 6}])

    differentagent = sim.build_agents(DifferentAgent, 'differentagent',
                                      agent_parameters=[{'agent_parameters': 0},
                                                        {'agent_parameters': 1},
                                                        {'agent_parameters': 2},
                                                        {'agent_parameters': 3},
                                                        {'agent_parameters': 4},
                                                        {'agent_parameters': 5},
                                                        {'agent_parameters': 6}])

    print('len', len(myagent))

    sim.advance_round(0)
    myagent.call_me_maybe()
    print('simple')

    for r in range(1, 14):
        sim.advance_round(r)
        myagent[r % 7].call_me_maybe()
        print('--')

    print('two individuals')
    for r in range(14, 28):
        sim.advance_round(r)
        (myagent[r % 7] + myagent[3]).call_me_maybe()
        print('--')

    print('one class')
    for r in range(28, 42):
        sim.advance_round(r)
        myagent[r % 7, 3].call_me_maybe()
        print('--')

    print('whole class plus individual')
    for r in range(42, 56):
        sim.advance_round(r)
        (myagent + myagent[r % 7]).call_me_maybe()
        print('--')

    print('two classes')
    for r in range(56, 70):
        sim.advance_round(r)
        (myagent + differentagent).call_me_maybe()
        print('--')

    sim.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=30)
    if (platform.system() != 'Windows' and
            platform.python_implementation() != 'PyPy'):
        main(processes=2, rounds=30)
