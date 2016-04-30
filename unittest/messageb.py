from __future__ import division
import abce


class MessageB(abce.Agent):
    def init(self, simulation_parameters, agent_parameters):
        # your agent initialization goes here, not in __init__
        pass

    def sendmsg(self):
        self.message('messagea', self.id, 'msg', 'hello there')

    def recvmsg(self):
        assert self.get_messages('msg')[0].content == 'hello there'
