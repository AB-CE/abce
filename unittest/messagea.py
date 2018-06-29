from __future__ import division
import abcEconomics


class MessageA(abcEconomics.Agent):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def sendmsg(self):
        self.send(('messageb', self.id), 'msg', 'hello there')

    def recvmsg(self):
        msg = self.get_messages('msg')[0]
        assert msg == 'hello there'
