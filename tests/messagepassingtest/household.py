from __future__ import division
import abcEconomics


class Household(abcEconomics.Agent, abcEconomics.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.create('money', 100)
        print(self.name)

    def one(self):
        pass

    def two(self):
        messages = self.get_messages("hello")
        print(self.name, messages)
        oo = self.get_offers('cookies')
        for offer in oo:
            self.accept(offer)
        print(self.name, 'cookies', self.possession(
            'cookies'), 'money', self.possession('money'))
