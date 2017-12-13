import abce
import time


class LoggerTest(abce.Agent):
    def init(self, rounds):
        self.last_round = rounds - 1
        self.create('money', 50)
        self.create('cookies', 3)

    def one(self):
        self.log('possessions', self.possessions())
        self.log('round_log', self.round)
        pass

    def two(self):
        pass

    def three(self):
        pass

    def clean_up(self):
        pass

    def all_tests_completed(self):
        if self.round == self.last_round:
            time.sleep(0.5)
            print('Check database whether logging succeeded')
