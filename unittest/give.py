from __future__ import division
import abceagent
from abcetools import *
import random


class Give(abceagent.Agent):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        abceagent.Agent.__init__(self, *_pass_to_engine)
        self.last_round = simulation_parameters['num_rounds'] - 1
        if self.idn == 1:
            self.tests = {'all': False, 'topic': False, 'biased': False}
        else:
            self.tests = {}

    def one(self):
        if self.idn == 0:
            self.create('cookies', random.uniform(0, 10000))
            self.cookies = self.possession('cookies')
            quantity = random.uniform(0, self.possession('cookies'))
            self.give('give', 1, 'cookies', quantity)
            assert self.possession('cookies') == self.cookies - quantity
            self.message('give', 1, topic='tpc', content=quantity)

    def two(self):
        if self.idn == 1:
            rnd = random.randint(0, 2)
            if rnd == 0:
                msg = self.get_messages_all()
                msg = msg['tpc']
                self.tests['all'] = True
            elif rnd == 1:
                msg = self.get_messages_biased('tpc')
                self.tests['biased'] = True
            elif rnd == 2:
                msg = self.get_messages('tpc')
                self.tests['topic'] = True
            assert len(msg) == 1
            msg = msg[0]
            assert msg.content == self.possession('cookies')
            assert msg.sender_group == 'give'
            assert msg.sender_idn == 0
            assert msg.topic == 'tpc'
            assert msg.receiver_idn == 1
            assert msg.receiver_group == 'give'

    def three(self):
        pass

    def clean_up(self):
        self.destroy_all('cookies')

    def all_tests_completed(self):
            assert all(self.tests.values()), self.tests
            if self.round == self.last_round and self.idn == 0:
                print('Test abceagent.give:\t\t\t\t\tOK')
                print('Test abceagent.message:\t\t\t\t\tOK')
                print('Test abceagent.get_messages:\t\t\t\tOK')
                print('Test abceagent.get_messages_all:\t\t\tOK')
                print('Test abceagent.get_messages_biased:\t\t\tOK')


