from __future__ import division
import abce
from abce.tools import *
import time


class LoggerTest(abce.Agent):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abce.Agent.__init__(self, **_pass_to_engine)
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
        pass

    def all_tests_completed(self):
        time.sleep(0.5)
        if self.round == self.last_round:
            print('Check database whether logging succeeded')



