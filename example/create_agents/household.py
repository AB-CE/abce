from __future__ import division
import abce


class Household(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        self.count = 1

    def print_id(self):
        #print(self.group, self.id)
        pass

    def receive_message(self):
        messages = self.get_messages('msg')
        assert len(messages) == 1, self.id
        assert messages[0].content == self.id, (self.id, messages[0].content)
