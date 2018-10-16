import abcEconomics
import random


class Give(abcEconomics.Agent):
    def init(self, rounds):
        self.last_round = rounds - 1
        if self.id == 1:
            self.tests = {'all': False, 'topic': False}
        else:
            self.tests = {}

    def one(self):
        if self.id == 0:
            self.create('cookies', random.uniform(0, 10000))
            self.cookies = self['cookies']
            quantity = random.uniform(0, self['cookies'])
            self.give(('give', 1), 'cookies', quantity)
            assert self['cookies'] == self.cookies - quantity
            self.send_envelope(('give', 1), topic='tpc', content=quantity)

    def two(self):
        if self.id == 1:
            rnd = random.randint(0, 1)
            if rnd == 0:
                msg = self.get_messages_all()
                msg = msg['tpc']
                self.tests['all'] = True
                assert len(msg) == 1, len(msg)
            elif rnd == 1:
                msg = self.get_messages('tpc')
                self.tests['topic'] = True
                assert len(msg) == 1, len(msg)
            msg = msg[0]
            assert msg.content == self['cookies']
            assert msg.sender == ('give', 0), msg.sender
            assert msg.topic == 'tpc'
            assert msg.receiver == ('give', 1)

    def three(self):
        pass

    def clean_up(self):
        self.destroy('cookies')

    def all_tests_completed(self):
        if self.time == self.last_round and self.id == 0:
            assert all(self.tests.values(
            )), 'not all tests have been run; abcEconomics workes correctly, restart the unittesting to do all tests %s' % self.tests
            print('Test abcEconomics.give:\t\t\t\t\tOK')
            print('Test abcEconomics.message:\t\t\t\tOK')
            print('Test abcEconomics.get_messages:\t\t\t\tOK')
            print('Test abcEconomics.get_messages_all:\t\t\tOK')
