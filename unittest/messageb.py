from __future__ import division
import abce


class MessageB(abce.Agent):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def sendmsg(self):
        self.send(('messagea', self.id), 'msg', 'hello there')

    def recvmsg(self):
        assert self.get_messages('msg')[0].content == 'hello there'
