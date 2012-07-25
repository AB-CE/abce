from __future__ import division
import abceagent
from abcetools import *
import time


class Logger(abceagent.Agent):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abceagent.Agent.__init__(self, *_pass_to_engine)
        self.last_round = simulation_parameters['num_rounds'] - 1
        self.create('money', 50)
        self.create('cookies', 3)

    def one(self):
        self.log('possessions', self.possessions(['money', 'cookies']))
        self.log_value('round_log', self.round)
        pass

    def two(self):
        pass

    def three(self):
        pass

    def clean_up(self):
        self.nested = {'money': 1, 'cookies': 1, 'nested': {'money': 2, 'cookies': 2, 'third': {'money': 3, 'cookies': 3}}}
        self.log_dict('table', self.nested)

    def all_tests_completed(self):
        time.sleep(0.5)
        if self.round == self.last_round:
            print('Check database whether logging succeeded')
            print('nested should represent', self.nested)



